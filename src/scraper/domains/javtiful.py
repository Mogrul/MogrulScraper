import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup

from enums import RequestType, ResponseType, PornDBCategory
from models import Request, DownloadRequest
from session import PornDB
from shared.util import sanitise_filename
from .domain import Domain

class Javtiful(Domain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            logger = logging.getLogger("Domain.Javtiful"),
            site_name = "javtiful",
            *args,
            **kwargs
        )

        self._porndb = PornDB()

    def run(self):
        if self._stop_event.is_set():
            return

        message = f"Scraping {self._url}"
        self._logger.info(message)
        self._send_terminal(f"{'[JAVTIFUL]':^15}" + message)

        if "/video/" in self._url:
            self._handle_video(self._url)

        if (
            "/actress/" in self._url
            or "/channel/" in self._url
        ):
            self._handle_album()

    def _handle_video(self, url: str, album_name: str | None = None) -> None:
        def get_code(soup: BeautifulSoup) -> str | None:
            title = soup.find("div", {"class": "front-watch-title mt-3"})
            if not title: return None

            h1 = title.find("h1")
            if not h1: return None

            title = h1.get_text()
            if not title: return None

            return title.split(" ")[0]

        if self._stop_event.is_set():
            return

        # Visit the page
        req = Request(
            url = url,
            request_type = RequestType.GET,
            response_type = ResponseType.SOUP,
        )
        res = self._session.send(req)

        if not res.soup:
            self._logger.error(f"Request didn't return soup object: {url}")
            return None

        script = res.soup.find("script", {"id": "frontWatchConfig"})

        if not script:
            return None

        try:
            video_config = json.loads(str(script.get_text()))

        except json.decoder.JSONDecodeError:
            self._logger.exception(f"Failed to decode video config to JSON: {url}")
            return None

        code = get_code(res.soup)

        if not code:
            self._logger.error(f"Failed to get code: {url}")
            return None

        sources = video_config.get("playerSources", [])
        try:
            source = sources[0]

        except IndexError:
            self._logger.exception(f"Failed to get first source in video config: {url}")
            return None

        direct_url = source.get("src")
        porndb_search = self._porndb.search(code)

        if not porndb_search:
            self._logger.warning(f"Failed to get porndb data: {url}")
            return None

        porn_db_data, category = porndb_search
        porn_db_data = porn_db_data.get("data")

        if not isinstance(porn_db_data, list):
            self._logger.warning(f"Failed to get porndb data: {url}")
            return None

        try:
            first_item: dict = porn_db_data[0]

        except IndexError:
            self._logger.warning(f"Failed to find first item in porndb data: {url}")
            return None

        date = first_item.get("date")
        title = first_item.get("title")
        site: dict = first_item.get("site", {})
        site_name = site.get("name")

        if (
            not date
            or not title
            or not site_name
        ):
            return None

        # Create the path for the file
        base_path = self._config.download_path / self._site_name / category.value
        if album_name:
            base_path = base_path / album_name

        if code not in title:
            title = f"{code.upper()} {title}"

        file_name_string = sanitise_filename(f"{site_name} {date} {title}"[:240]) + ".mp4"
        file_name_path = Path(file_name_string)

        if self._stop_event.is_set():
            return

        re = DownloadRequest(
            url = direct_url,
            destination = base_path / file_name_path
        )
        self._session.download(re, self._stop_event)

    def _handle_album(self):
        def get_max_page_num(soup: BeautifulSoup) -> int:
            pagination = soup.find("a", {"class": "front-pagination-link is-active"})

            if not pagination:
                return 1

            try:
                return int(pagination.get_text())

            except ValueError:
                return 1

        def get_urls_in_page(page_num: int) -> list[str]:
            page_urls = []

            # Get page
            preq = Request(
                url = self._url,
                request_type = RequestType.GET,
                response_type = ResponseType.SOUP,
                params = {
                    "page": page_num
                }
            )
            pres = self._session.send(preq)

            if not pres.soup:
                return page_urls

            articles = pres.soup.select(
                "article.front-video-card:not(.front-partner-card)"
            )

            for article in articles:
                a = article.find("a")
                if not a: continue
                url = "https://javtiful.com" + str(a.get("href"))
                page_urls.append(url)

            return page_urls

        def get_name(soup: BeautifulSoup) -> str | None:
            div = soup.find("div", {"class": "front-actress-detail-head"})
            if not div: return None

            h2 = div.find("h2")
            if not h2: return None

            return str(h2.get_text())

        # Visit last page to get max page number
        req = Request(
            url = self._url,
            request_type = RequestType.GET,
            response_type = ResponseType.SOUP,
            params = {
                "page": "999"
            }
        )
        res = self._session.send(req)

        if not res.soup:
            self._logger.error(f"{res.status_code}: {self._url}?page=999")
            return

        name = get_name(res.soup)

        if not name:
            self._logger.error(f"[NAME FAIL]: {self._url}?page=999")
            return

        # Retrieve all page urls using a thread pool
        max_page_num = get_max_page_num(res.soup)
        urls: list[str] = []
        with ThreadPoolExecutor(
            max_workers = self._config.concurrent,
            thread_name_prefix = "Domain.Javtiful.Thread"
        ) as executor:
            futures = [
                executor.submit(get_urls_in_page, page_num)
                for page_num in range(1, max_page_num + 1)
            ]

            for future in as_completed(futures):
                try:
                    urls_in_page = future.result()

                except Exception as e:
                    self._logger.exception(f"Exception on getting page URLs: {e}")
                    continue

                urls.extend(urls_in_page)

        # Sanitise URLs to prefer reduced mosaic
        for video_url in urls.copy():
            if video_url.endswith("-reducing-mosaic"):
                normal_url = video_url.removesuffix("-reducing-mosaic")

                if normal_url in urls:
                    urls.remove(normal_url)

        self._logger.info(f"Found {len(urls)} URLs")
        urls = list(set(urls)) # Remove duplicates

        # Add urls to video handler using thread pool
        with ThreadPoolExecutor(
            max_workers = self._config.concurrent,
            thread_name_prefix = "Domain.Javtiful.Thread"
        ) as executor:
            futures = [
                executor.submit(self._handle_video, url)
                for url in urls
            ]

            for future in as_completed(futures):
                # Cancel pending if stop event
                if self._stop_event.is_set():
                    for future in futures:
                        future.cancel()

                    return

                try:
                    future.result()

                except Exception as e:
                    self._logger.exception(f"Exception on handling video from album: {e}")
                    continue