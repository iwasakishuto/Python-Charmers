#coding: utf-8
import pandas as pd
import datetime
import MySQLdb
from MySQLdb.cursors import Cursor
from typing import Any,Optional,Callable,Union,List,Tuple,Dict

from ..utils._colorings import toBLUE, toGREEN, toRED
from ..utils.environ_utils import check_environ
from ..utils.generic_utils import handleKeyError
from .base import PycharmersSQL

class PycharmersMySQL(PycharmersSQL):
    """Wrapper class for MySQL.

    Args:
        host (Optional[str], optional)     : host to connect. Defaults to ``None``.
        password (Optional[str], optional) : user to connect as. Defaults to ``None``.
        user (Optional[str], optional)     : password to use. Defaults to ``None``.
        database (Optional[str], optional) : database to use. Defaults to ``None``.
        verbose (bool, optional)           : Whether to print message or not Defaults to ``False``.
    """
    def __init__(self, host:Optional[str]=None, password:Optional[str]=None, user:Optional[str]=None, database:Optional[str]=None, verbose:bool=False):
        super().__init__(
            api_name="MySQL",
            verbose=verbose,
            host=host, password=password, user=user, database=database,
        )

    def connect(self, func:Callable, host:Optional[str]=None, password:Optional[str]=None, user:Optional[str]=None, database:Optional[str]=None, **kwargs) -> Union[pd.DataFrame, Tuple[tuple], None]:
        """Use ``MySQLdb.connect`` to create a connection to the database, and close it after excuting ``func`` .

        Args:
            func (Callable)                    : The function you want to execute. Receive ``cursor`` as the first argument.
            host (Optional[str], optional)     : host to connect. Defaults to ``None``.
            password (Optional[str], optional) : user to connect as. Defaults to ``None``.
            user (Optional[str], optional)     : password to use. Defaults to ``None``.
            database (Optional[str], optional) : database to ues. Defaults to ``None``.
            kwargs (dict)                      : See a table below.

        Returns:
            Any: Return value of ``func``

        Keyword arguments for ``MySQLdb.connect`` is below.

        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        |          Name          |   Type   |                                                                                                                                      Description                                                                                                                                       |
        +========================+==========+========================================================================================================================================================================================================================================================================================+
        | ``port``               | ``int``  | TCP/IP port to connect to                                                                                                                                                                                                                                                              |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``unix_socket``        | ``str``  | location of unix_socket to use                                                                                                                                                                                                                                                         |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``conv``               | ``dict`` | conversion dictionary, see MySQLdb.converters                                                                                                                                                                                                                                          |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``connect_timeout``    | ``int``  | number of seconds to wait before the connection attempt fails.                                                                                                                                                                                                                         |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``compress``           | ``bool`` | if set, compression is enabled                                                                                                                                                                                                                                                         |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``named_pipe``         | ``str``  | if set, a named pipe is used to connect (Windows only)                                                                                                                                                                                                                                 |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``init_command``       | ``str``  | command which is run once the connection is created                                                                                                                                                                                                                                    |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``read_default_file``  | ``str``  | file from which default client values are read                                                                                                                                                                                                                                         |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``read_default_group`` | ``str``  | configuration group to use from the default file                                                                                                                                                                                                                                       |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``cursorclass``        | ``type`` | class object, used to create cursors (keyword only)                                                                                                                                                                                                                                    |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``use_unicode``        | ``bool`` | If ``True``, text-like columns are returned as unicode objects using the connection``'s character set. Otherwise, text-like columns are returned as bytes. Unicode objects will always be encoded to the connection'``s character set regardless of this setting. Default to ``True``. |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``charset``            | ``str``  | If supplied, the connection character set will be changed to this character set.                                                                                                                                                                                                       |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``auth_plugin``        | ``str``  | If supplied, the connection default authentication plugin will be changed to this value. Example values are ``mysql_native_password`` or ``caching_sha2_password``                                                                                                                     |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``sql_mode``           | ``str``  | If supplied, the session SQL mode will be changed to this setting. For more details and legal values, see the MySQL documentation.                                                                                                                                                     |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``client_flag``        | ``int``  | flags to use or 0 (see MySQL docs or constants/CLIENTS.py)                                                                                                                                                                                                                             |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``ssl_mode``           | ``str``  | specify the security settings for connection to the server; see the MySQL documentation for more details (mysql_option(), MYSQL_OPT_SSL_MODE). Only one of ``'DISABLED'``, ``'PREFERRED'``, ``'REQUIRED'``, ``'VERIFY_CA'``, ``'VERIFY_IDENTITY'`` can be specified.                   |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``ssl``                | ``dict`` | dictionary or mapping contains SSL connection parameters; see the MySQL documentation for more details (mysql_ssl_set()).  If this is set, and the client does not support SSL, NotSupportedError will be raised.                                                                      |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``local_infile``       | ``bool`` | enables LOAD LOCAL INFILE; zero disables                                                                                                                                                                                                                                               |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``autocommit``         | ``bool`` | If False (default), autocommit is disabled. If ``True``, autocommit is enabled. If None, autocommit isn't set and server default is used.                                                                                                                                              |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``binary_prefix``      | ``bool`` | If set, the ``'_binary'`` prefix will be used for raw byte query arguments (e.g. Binary). This is disabled by default.                                                                                                                                                                 |
        +------------------------+----------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        check_environ(
            required_keynames=self.required_keynames,
            required_env_varnames=self.required_env_varnames,
            host=host, password=password, user=user, database=database,
        )
        connection = MySQLdb.connect(
            host=self.get_val("host", host=host),
            password=self.get_val("password", password=password),
            user=self.get_val("user", user=user),
            database=self.get_val("database", database=database),
            use_unicode=True, charset="utf8", cursorclass=Cursor,
        )
        cursor = connection.cursor()
        ret = func(cursor=cursor, **kwargs)
        cursor.close()
        connection.commit()
        connection.close()
        return ret