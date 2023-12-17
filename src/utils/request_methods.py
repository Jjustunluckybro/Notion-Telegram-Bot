from typing import NamedTuple


class RequestMethods(NamedTuple):
    GET: str = "GET"
    POST: str = "POST"
    PATCH: str = "PATCH"
    DELETE: str = "DELETE"
