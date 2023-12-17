class StorageException(ValueError):
    """Base exception for all storage exceptions"""
    ...


class UnacceptableResponseStatusCode(StorageException):
    ...


class StorageNotFound(StorageException):
    ...
