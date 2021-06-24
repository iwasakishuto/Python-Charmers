#coding: utf-8
from ._colorings import toBLUE, toGREEN

__all__ = [
    "PythonCharmersImprementationWarning", 
    "DriverNotFoundWarning",
    "EnvVariableNotDefinedWarning"
]

class PythonCharmersImprementationWarning(Warning):
    """ 
    Warnings that developers will resolve. 
    Developers are now solving in a simple stupid way.
    """

class DriverNotFoundWarning(Warning):
    """
    Warnings when launching all supported drivers fails.
    """
    def __init__(self, message):
        super().__init__(message)
        print(
            "Could not create an instance of the Selenium WebDriver. If you want " + \
            "to check the error logs, please call " + toBLUE("pycharmers.utils.get_driver") + \
            " with specifying the " + toGREEN("driver_type") + " you want to look up." + \
            "If you can not prepare Selenium WebDriver by yourself, please build the environment using Docker." + \
            "Please see " + toBLUE("https://github.com/iwasakishuto/Python-Charmers/tree/master/docker")
        )

class EnvVariableNotDefinedWarning(Warning):
    """
    Warnings when necessary environment variables are not defined. Use ``write_environ`` function to define them.

    Examples:
        >>> from pycharmers.utils import write_environ
        >>> write_environ(
        ...     PYTHON_CHARMERS_API_TRELLO_ID     = "id",
        ...     PYTHON_CHARMERS_API_TRELLO_APIKEY = "apikey",
        ...     PYTHON_CHARMERS_API_TRELLO_TOKEN  = "token",
        >>> )
    """