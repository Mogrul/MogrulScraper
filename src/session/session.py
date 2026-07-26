import logging
import time
import uuid
from threading import Event

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

from enums import RequestType, Status, ResponseType, EventDownloadType
from models import Request, Response, Download, DownloadRequest, EventDownload, EventTerminal
from shared import SingletonMeta, Config
from shared.util import format_duration, format_bytes


class Session(metaclass = SingletonMeta):
    def __init__(self):
        self._logger = logging.getLogger("Session")
        self._config = Config()
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/150.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml"
                ";q=0.9,image/avif,image/webp,image/apng,*/*"
                ";q=0.8"
            )
        })

        _adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
        )
        self._session.mount("session://", _adapter)
        self._session.mount("https://", _adapter)

        # ID -> Download
        self._downloads: dict[str, Download] = {}

    def send(self, request: Request) -> Response:
        try:
            if request.request_type == RequestType.POST:
                r = self._session.post(
                    url = request.url,
                    headers = request.headers,
                    json = request.json,
                    params = request.params,
                    timeout = self._config.timeout,
                )

            elif request.request_type == RequestType.GET:
                r = self._session.get(
                    url = request.url,
                    headers = request.headers,
                    params = request.params,
                    timeout = self._config.timeout,
                )

        except requests.exceptions.Timeout:
            return Response(
                request.url,
                status = Status.ERROR_TIMEOUT,
                headers = request.headers,
                params = request.params,
                json = request.json,
            )

        self._logger.debug(f"{r.status_code:<10} {r.url}")

        if r.status_code != 200:
            return Response(
                request.url,
                status = Status.ERROR,
                headers = dict(r.headers),
                params = dict(request.params),
            )

        match request.response_type:
            case ResponseType.TEXT:
                return Response(
                    request.url,
                    status = Status.OK,
                    headers = dict(r.headers),
                    params = dict(request.params),
                    text = r.text,
                )

            case ResponseType.JSON:
                try:
                    return Response(
                        request.url,
                        status = Status.OK,
                        headers = dict(r.headers),
                        params = dict(request.params),
                        json = r.json(),
                    )

                except requests.exceptions.JSONDecodeError:
                    return Response(
                        request.url,
                        status = Status.ERROR_JSON,
                        headers = dict(r.headers),
                        params = dict(request.params),
                        text = r.text,
                    )

            case ResponseType.SOUP:
                try:
                    return Response(
                        request.url,
                        status = Status.OK,
                        headers = dict(r.headers),
                        params = dict(request.params),
                        soup = BeautifulSoup(r.text, "html.parser"),
                    )

                except TypeError:
                    return Response(
                        request.url,
                        status = Status.ERROR_SOUP,
                        headers = dict(r.headers),
                        params = dict(request.params),
                        text = r.text,
                    )

    def download(self, request: DownloadRequest, stop_event: Event):
        if stop_event.is_set():
            return

        headers = request.headers
        destination = request.destination

        if destination.exists():
            self._logger.info(f"{request.destination} already exists, skipping...")
            return

        # Get current downloaded bytes if need to resume
        temp_path = destination.with_suffix(destination.suffix + ".tmp")
        downloaded_bytes = 0
        if temp_path.exists():
            downloaded_bytes = temp_path.stat().st_size
            headers["Range"] = f"bytes={downloaded_bytes}-"

        temp_path.parent.mkdir(parents = True, exist_ok = True)

        # Start the download
        with self._session.get(
            url = request.url,
            headers = headers,
            timeout = self._config.timeout,
            stream = True,
            params = request.params,
        ) as r:
            if r.status_code not in (200, 206):
                self._logger.warning(f"{r.status_code:<10} Failed to download: {request.url}")
                return

            start_time = time.perf_counter()
            id = str(uuid.uuid5(uuid.NAMESPACE_URL, request.url))
            mode = "ab" if downloaded_bytes else "wb"
            total_bytes = r.headers.get("Content-Length", 0)
            total_bytes = int(total_bytes) + downloaded_bytes if total_bytes else 0
            download_percent = self._get_percentage(downloaded_bytes, total_bytes)

            download = Download(id, destination.name, download_percent)
            self._add_download(download)

            self._logger.info(
                f"{format_bytes(total_bytes):^10} Downloading: {destination}"
            )

            with open(temp_path, mode) as f:
                for chunk in r.iter_content(chunk_size = self._config.chunk_size):
                    if stop_event.is_set():
                        break

                    if chunk:
                        f.write(chunk)

                    downloaded_bytes += len(chunk)
                    download_percent = self._get_percentage(downloaded_bytes, total_bytes)
                    self._update_progress(download, download_percent)

        # Handle download completion
        self._remove_download(download)
        if stop_event.is_set():
            return

        temp_path.rename(destination)

        time_taken = time.perf_counter() - start_time

        from web.routes import send_client
        message = f"{format_duration(time_taken):^10}{format_bytes(downloaded_bytes):^10} Downloaded {destination}"
        send_client(EventTerminal(message))
        self._logger.info(message)

    def get_download_events(self) -> list[EventDownload]:
        download_events = []

        for download in self._downloads.values():
            download_events.append(EventDownload(
                type = EventDownloadType.ADD,
                id = download.id,
                name = download.name,
                progress = download.progress,
            ))

        return download_events

    def _update_progress(self, download: Download, progress: int) -> bool:
        current_download = self._downloads.get(download.id)

        if current_download is None:
            return False

        if current_download.progress == progress:
            return False

        current_download.progress = progress

        if self._config.web_client:
            from web.routes import send_client

            send_client(EventDownload(
                type = EventDownloadType.PROGRESS,
                id = download.id,
                name = download.name,
                progress = progress,
            ))

        return True

    def _add_download(self, download: Download) -> bool:
        if download.id in self._downloads:
            return False

        if self._config.web_client:
            from web.routes import send_client

            send_client(EventDownload(
                type = EventDownloadType.ADD,
                id = download.id,
                name = download.name,
                progress = download.progress,
            ))

        self._downloads[download.id] = download
        return True

    def _remove_download(self, download: Download) -> bool:
        deleted = self._downloads.pop(download.id, None)

        if deleted is None:
            return False

        if self._config.web_client:
            from web.routes import send_client

            send_client(EventDownload(
                type = EventDownloadType.COMPLETE,
                id = download.id,
                name = download.name,
                progress = download.progress,
            ))

        return True

    def _get_percentage(self, downloaded_bytes: int, total_bytes: int) -> int:
        return (
            int(downloaded_bytes / total_bytes * 100)
            if total_bytes > 0
            else 0
        )