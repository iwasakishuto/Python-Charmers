"""Base class for Python-Charmers' SDK """
#coding: utf-8
import os
from abc import ABC
from ..utils._path import DOTENV_PATH
from ..utils.environ_utils import name2envname, load_environ
from ..utils.generic_utils import verbose2print

class PycharmersSDK(ABC):
    """Abstract Class for Python-Charmers API
    
    Args:
        env_path (str)     : path/to/.env (default= ``DOTENV_PATH``)
        service_name (str) : The service name.
        verbose (bool)     : Whether to print message or not. (default= ``False``) 
        \*\*kwargs (dict)    : Required Keywords.

    Attributes:
        print (function)             : Print function based on ``verbose``
        service_name (str)           : The service name
        required_env_varnames (list) : The required env varnames.
        kwargs (dict)                : Keyword arguments.
    """
    def __init__(self, env_path=DOTENV_PATH, api_name="", verbose=True, **kwargs):
        self.api_name = api_name
        required_keynames = list(kwargs.keys())
        required_env_varnames = [self.keyname2envname(k) for k in required_keynames]
        load_environ(
            dotenv_path=env_path, 
            env_varnames=required_env_varnames, 
            verbose=verbose,
        )
        self.print = verbose2print(verbose)
        self.kwargs = kwargs
        self.required_keynames = required_keynames
        self.required_env_varnames = required_env_varnames

    def keyname2envname(self, keyname):
        """Convert keyname to environment varname.

        Args
            keyname (str) : Keyname for method.

        Examples:
            >>> from pycharmers.sdk._base import PycharmersSDK
            >>> sdk = PycharmersSDK()
            >>> sdk.keyname2envname("id")
            'TRANSLATION_GUMMY_GATEWAY_USELESS_NAME'
            >>> sdk.keyname2envname("hoge")
            'TRANSLATION_GUMMY_GATEWAY_USELESS_HOGE'
        """
        return name2envname(name=keyname, prefix=self.api_name, service="sdk")

    def get_val(self, keyname, **kwargs):
        """Get the value from ``gatewaykwargs`` or an environment variable.

        Args:
            keyname (str)     : Keyname for each method.
            \*\*kwargs (dict)   : Given ``kwargs``.

        Examples:
            >>> from pycharmers.sdk._base import PycharmersSDK
            >>> sdk = PycharmersSDK()
            >>> print(sdk.get_val("hoge"))
            None
            >>> print(sdk.get_val("username"))
            USERNAME_IN_ENVFILE
            >>> print(gateway.get_val("username", username=":)"))
            :)
        """
        return kwargs.get(keyname) or os.getenv(self.keyname2envname(keyname))
