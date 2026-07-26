import logging
import os
from wsgiref import headers

from enums import PornDBCategory, ResponseType, RequestType
from models import Request, Response
from session import Session
from shared import SingletonMeta, Config


class PornDB(metaclass = SingletonMeta):
    def __init__(self):
        self._logger = logging.getLogger("PornDB")
        self._session = Session()
        self._config = Config()

        self._headers = {
            "Authorization": f"Bearer {self._config.porndb_token}",
        }
        self._url = "https://api.theporndb.net"

    def search(self, code: str) -> tuple[dict, PornDBCategory] | None:
        for category in PornDBCategory:
            data = self.search_category(category, code)
            if data:
                return data, category

        return None

    def search_category(self, category: PornDBCategory, code: str) -> dict:
        url = f"{self._url}/{category.value}"
        param = "parse" if category != PornDBCategory.JAV else "external_id"
        req = Request(
            url = url,
            request_type = RequestType.GET,
            response_type = ResponseType.JSON,
            headers = self._headers,
            params = {
                param: code,
            }
        )
        res = self._session.send(req)
        if not res.json:
            return {}
        return res.json