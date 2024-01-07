class StorageException(ValueError):
    """Base exception for all storage exceptions"""
    ...


class UnexpectedResponse(StorageException):
    ...


class StorageNotFound(StorageException):
    ...


class StorageValidationError(StorageException):
    ...


class StorageInvalidId(StorageValidationError):
    ...


class StorageDuplicate(StorageException):
    ...
