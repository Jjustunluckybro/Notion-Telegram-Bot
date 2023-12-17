import asyncio
import json
from abc import ABC, abstractmethod
from logging import getLogger

from aiogram.client.session import aiohttp
from aiohttp import ClientResponse
from pydantic import BaseModel
from src import config
from src.utils import statuses
from src.utils.request_methods import RequestMethods
from src.utils.exceptions.request import AuthException


class ResponseModel(BaseModel):
    body: str
    status: int


class IRequestHandler(ABC):

    @abstractmethod
    async def get(self, url: str) -> ResponseModel:
        """GET request"""
        ...

    @abstractmethod
    async def post(self, url: str, body: dict) -> ResponseModel:
        """POST request"""
        ...

    @abstractmethod
    async def patch(self, url: str, body: dict) -> ResponseModel:
        """PATCH request"""
        ...

    @abstractmethod
    async def delete(self, url: str, body: dict) -> ResponseModel:
        """DELETE request"""
        ...


class RequestHandler(IRequestHandler):
    _token = str | None
    _available_methods = RequestMethods

    def __init__(self, host: str = config.BACKEND_HOST):
        """

        :param host: backend host
        """
        self._logger = getLogger(f"app.request_handler")
        self.host = host

    @staticmethod
    async def parce_response(r: ClientResponse) -> ResponseModel:
        """Parce ClientResponse obj to ResponseModel obj"""
        status = r.status
        details: str = await r.text()
        return ResponseModel(body=details, status=status)

    async def get_auth_header(self) -> dict:
        return {"Authorization": f"bearer {self._token}"}

    async def auth(self) -> None:
        """Auth with backend. Get JWT token and write it to class "_token" protected var"""
        cred = {
            "username": config.BACKEND_USER_LOGIN,
            "password": config.BACKEND_USER_PASSWORD,
        }

        r = await self.post("auth/jwt/login", data=cred)
        if r.status == statuses.SUCCESS_200:
            r_body = json.loads(r.body)
            self.__class__._token = r_body["access_token"]
            self._logger.info(f"Successfully update auth token")
        else:
            self._logger.critical(f"Auth was failed: {r.body}")
            raise AuthException(status=r.status, msg=r.body)

    async def check_response_auth_and_try_new_request(self, response: ResponseModel, method: str, url: str, *args,
                                                      **kwargs) -> ResponseModel:
        """
        Check response and if it has 401 status code, then make auth request and new request with input method and url
        :param response: Response to check
        :param method: one of _available_methods value
        :param url: Url to new request after auth
        :param args: For "POST", "PATCH", "DELETE"
        :param kwargs: For "POST", "PATCH", "DELETE"
        :return: Input response if not 401 status code or new request response
        """
        if response.status != statuses.UNAUTHORIZED_401:
            return response

        await self.auth()
        match method:
            case self._available_methods.GET:
                res = await self.get(url)
                return res
            case self._available_methods.POST:
                res = await self.post(url, *args, **kwargs)
                return res
            case self._available_methods.PATCH:
                res = await self.patch(url, *args, **kwargs)
                return res
            case self._available_methods.DELETE:
                res = await self.delete(url, *args, **kwargs)
                return res

    async def get(self, url: str) -> ResponseModel:
        """"""
        input_url = url
        url = f"{self.host}/{url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.get_auth_header()) as r:
                self._logger.info(f"GET/ send request - url: {url}")
                response = await self.parce_response(r)
                self._logger.info(
                    f"GET/ get response - url: {url} - status: {response.status}. details: {response.body}"
                )

        result = await self.check_response_auth_and_try_new_request(response=response,
                                                                    method=self._available_methods.GET,
                                                                    url=input_url)
        return result

    async def post(self, url: str, body: dict = None, data: dict = None) -> ResponseModel:
        """"""
        input_url = url
        url = f"{self.host}/{url}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, data=data) as r:
                self._logger.info(f"POST/ send request - url: {url}")
                response = await self.parce_response(r)
                self._logger.info(
                    f"POST/ get response - url: {url} - status: {response.status}. details: {response.body}"
                )

        result = await self.check_response_auth_and_try_new_request(response=response,
                                                                    method=self._available_methods.POST,
                                                                    url=input_url,
                                                                    json=body,
                                                                    data=data)
        return result

    async def patch(self, url: str, body: dict = None, data: dict = None) -> ResponseModel:
        """"""
        input_url = url
        url = f"{self.host}/{url}"

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, json=body) as r:
                self._logger.info(f"PATCH/ send request - url: {url}")
                response = await self.parce_response(r)
                self._logger.info(
                    f"PATCH/ get response - url: {url} - status: {response.status}. details: {response.body}"
                )

        result = await self.check_response_auth_and_try_new_request(response=response,
                                                                    method=self._available_methods.PATCH,
                                                                    url=input_url,
                                                                    json=body,
                                                                    data=data)
        return result

    async def delete(self, url: str, body: dict = None, data: dict = None) -> ResponseModel:
        input_url = url
        url = f"{self.host}/{url}"

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, json=body) as r:
                self._logger.info(f"DELETE/ send request - url: {url}")
                response = await self.parce_response(r)
                self._logger.info(
                    f"DELETE/ get response - url: {url} - status: {response.status}. details: {response.body}"
                )

        result = await self.check_response_auth_and_try_new_request(response=response,
                                                                    method=self._available_methods.DELETE,
                                                                    url=input_url,
                                                                    json=body,
                                                                    data=data)
        return result


def get_request_handler() -> RequestHandler:
    return RequestHandler()
