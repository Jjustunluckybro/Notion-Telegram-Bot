from typing import Any


class RequestException(ValueError):
    status: int
    """
    Any request exception
    """

    def __init__(self, status: int, msg: str, *args, **kwargs) -> None:
        super().__init__(msg, *args, *kwargs)
        self.status = status


class AuthException(RequestException):
    """
    Raise when some auth problem
    """
    ...


class ResponseValidationException(RequestException):
    """
    Raise when response has invalid data
    """

    def __init__(self,
                 status: int,
                 request_type: str,
                 url: str,
                 body: Any,
                 *args, **kwargs) -> None:
        exception_msg = f"{request_type}/ invalid response {url}, unexpected body: {body}"
        super().__init__(status, exception_msg, *args, *kwargs)
