class ConfigurateException(ValueError):
    """Parent exception for all errors with any program configuration"""


class EnvDependNotFound(ConfigurateException):
    """exception with env variables when it not found"""

    def __init__(self, depend_name: str):
        err_string = f"Not found env depend: {depend_name}"
        super().__init__(err_string)
