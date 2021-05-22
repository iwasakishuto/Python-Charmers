#coding: utf-8
import MySQLdb
from MySQLdb.cursors import Cursor
import pandas as pd
from typing import Any,Optional,Callable,Union,List,Tuple

from ..utils._colorings import toBLUE, toGREEN, toRED
from ..utils.environ_utils import check_environ
from ..utils.generic_utils import handleKeyError
from ._base import PycharmersAPI

class PycharmersMySQL(PycharmersAPI):
    """Wrapper class for MySQL.

    Args:
        host (Optional[str], optional)     : host to connect. Defaults to ``None``.
        password (Optional[str], optional) : user to connect as. Defaults to ``None``.
        user (Optional[str], optional)     : password to use. Defaults to ``None``.
        database (Optional[str], optional) : database to ues. Defaults to ``None``.
        verbose (bool, optional)           : Whether to print message or not Defaults to ``False``.
    """
    def __init__(self, host:Optional[str]=None, password:Optional[str]=None, user:Optional[str]=None, database:Optional[str]=None, verbose:bool=False):
        super().__init__(
            api_name="MySQL", 
            verbose=verbose,
            host=host, password=password, user=user, database=database,
        )

    @staticmethod
    def format_data(data:Any, type:str) -> str:
        """Format python data to match sql data format

        Args:
            data (Any): Python any data.
            type (str): SQL data type. (ex. ``"int(11)"``, ``"varchar(100)"``)

        Returns:
            str: Correctly formatted python data.

        Examples:
            >>> import datetime
            >>> from pycharmers.api import PycharmersMySQL
            >>> PycharmersMySQL.format_data(data=1, type="int(8)")
                '1'
            >>> PycharmersMySQL.format_data(data=1, type="varchar(10)")
                '"1"'
            >>> PycharmersMySQL.format_data(data=datetime.datetime(1998,7,3), type="datetime")
                '"1998-07-03 00:00:00"'
        """
        if type.startswith("datetime") and (not isinstance(data, str)):
            data = data.strftime("%Y-%m-%d %H:%M:%S")
        if type.startswith("int"):
            data = str(data)
        else:
            data = f'"{data}"'
        return data
    
    def connect(self, func:Callable, host:Optional[str]=None, password:Optional[str]=None, user:Optional[str]=None, database:Optional[str]=None, **kwargs) -> Union[pd.DataFrame, Tuple[tuple], None]:
        """Use ``MySQLdb.connect`` to create a connection to the database, and close it after excuting ``func`` .

        Args:
            func (Callable)                    : The function you want to execute. Receive ``cursor`` as the first argument.
            host (Optional[str], optional)     : host to connect. Defaults to ``None``.
            password (Optional[str], optional) : user to connect as. Defaults to ``None``.
            user (Optional[str], optional)     : password to use. Defaults to ``None``.
            database (Optional[str], optional) : database to ues. Defaults to ``None``.
            \*\*kwargs (dict)                     : See a table below.

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

    def execute(self, query:str, columns:list=[], verbose:bool=False) -> Union[pd.DataFrame, Tuple[tuple], None]:
        """Execute a SQL query.

        Args:
            query (str)              : Query to execute on server.
            columns (list, optional) : If this value is fiven, Return value will be as a ``pd.DataFrame`` format. Defaults to ``[]``.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            Union[pd.DataFrame, Tuple[tuple], None]: Return value of query.

        Examples:
            >>> from pycharmers.api import PycharmersMySQL
            >>> sql = PycharmersMySQL()
            >>> sql.execute("show databases;")
            (('information_schema',),
             ('mysql',),
             ('performance_schema',),
             ('remody',),
             ('sys',))
            >>> sql.execute("show databases;", columns=["name"])
            	    name
                0	information_schema
                1	mysql
                2	performance_schema
                3	remody
                4	sys
        """
        if verbose: print(query)
        def execute_query(cursor:Cursor) -> Tuple[tuple]:
            cursor.execute(query)
            return cursor.fetchall()
        ret = self.connect(func=execute_query)
        if len(columns)>0:
            ret = pd.DataFrame(data=ret, columns=columns)
        return ret

    def describe(self, table:str, verbose:bool=False) -> pd.DataFrame:
        """Get table structure.

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Table structure.
        """
        return self.execute(f"DESCRIBE {table};", columns=["Field","Type","Null","Key","Default","Extra"], verbose=verbose)

    def get_colnames(self, table:str, col_type:str="all") -> list:
        """Get column names in the specified ``table`` .

        Args:
            table (str)              : The name of table.
            col_type (str, optional) : What types columns to extract. Defaults to ``"all"``.

        Returns:
            list: Extracted Columns.
        """
        handleKeyError(lst=["all", "minimum", "input_field"], col_type=col_type)
        df = self.describe(table=table)
        if col_type=="all":
            pass
        elif col_type=="minimum":
            df = df[(df.Extra!="auto_increment") & (df.Null=="NO")]
        elif col_type=="input_field":
            df = df[df.Extra!="auto_increment"]
        return df.Field.to_list()

    def show_tables(self, verbose:bool=False) -> pd.DataFrame:
        """Show all tables.

        Args:
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Information for all Tables.
        """
        return self.execute("show table status;", columns=['Name', 'Engine', 'Version', 'Row_format', 'Rows', 'Avg_row_length', 'Data_length', 'Max_data_length', 'Index_length', 'Data_free', 'Auto_increment', 'Create_time', 'Update_time', 'Check_time', 'Collation', 'Checksum', 'Create_options', 'Comment'], verbose=verbose)

    def count_rows(self, table:str, verbose:bool=True) -> int:
        """Get the number of rows in the ``table`` .

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            int: The number of rows in the specified ``table`` .
        """
        return self.execute(f"SELECT count(*) FROM {table};")[0][0]

    def selectAll(self, table:str, verbose:bool=False) -> pd.DataFrame:
        """Select All records.

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: All records.
        """
        return self.execute(f"SELECT * FROM {table};", columns=self.get_colnames(table=table, col_type="all"), verbose=verbose)

    def insert(self, cursor:Cursor, table:str, data:List[list], columns:list=[], col_type="input_field") -> int:
        """Insert a record to specified ``table``

        Args:
            cursor (Cursor)          : Cursor
            table (str)              : The name of the table.
            data (List[list])        : Data to be inserted.
            columns (list, optional) : Column names to be inserted values. Defaults to ``[]``.
            col_type (str, optional) : If ``columns`` has no data, use :meth:`get_colnames <pycharmers.api.mysql.PycharmersMySQL.get_colnames>` to decide which columns to be inseted. Defaults to ``"input_field"``.

        Returns:
            int: The number of rows in ``table``
        """
        if len(columns)==0:
            columns = self.get_colnames(table=table, col_type=col_type)
        if not isinstance(data[0], list):
            data = [data]
        df_field = self.describe(table=table)
        coltypes = df_field.set_index("Field").filter(items=columns, axis=0).Type
        values = ", ".join([f"({', '.join([self.format_data(e,t) for e,t in zip(d,coltypes)])})" for d in data])
        return self.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES {values}")
