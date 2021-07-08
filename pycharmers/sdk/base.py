"""Base class for Python-Charmers' SDK """
#coding: utf-8
import os
import pandas as pd
from abc import ABC, abstractmethod
from ..utils._path import DOTENV_PATH
from ..utils.environ_utils import name2envname, load_environ, check_environ
from ..utils.generic_utils import verbose2print, handleKeyError
from ..utils._colorings import toBLUE, toGREEN, toRED

from typing import Any,Optional,Callable,Union,List,Tuple,Dict

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
    def __init__(self, env_path:str=DOTENV_PATH, api_name:str="", verbose:bool=True, **kwargs):
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

class PycharmersSQL(PycharmersSDK):
    """Wrapper class for Sqlite.

    Args:
        database (Optional[str], optional) : database to use. Defaults to ``None``.
        verbose (bool, optional)           : Whether to print message or not Defaults to ``False``.
    """
    def __init__(self, api_name:str="SQL", verbose:bool=False, **kwargs):
        super().__init__(
            api_name=api_name,
            verbose=verbose,
            **kwargs
        )

    @staticmethod
    def format_data(data:Any, type:str) -> str:
        """Format python data to match sql data format.

        Args:
            data (Any): Python any data.
            type (str): SQL data type. (ex. ``"int(11)"``, ``"varchar(100)"``)

        Returns:
            str: Correctly formatted python data.

        Examples:
            >>> import datetime
            >>> from pycharmers.sdk import PycharmersSQL
            >>> PycharmersSQL.format_data(data=1, type="int(8)")
                '1'
            >>> PycharmersSQL.format_data(data=1, type="varchar(10)")
                '"1"'
            >>> PycharmersSQL.format_data(data=datetime.datetime(1998,7,3), type="datetime")
                '"1998-07-03 00:00:00"'
        """
        if type.startswith("datetime") and (not isinstance(data, str)):
            data = data.strftime("%Y-%m-%d %H:%M:%S")
        if type.startswith("int") or ("now()" in data):
            data = str(data)
        else:
            data = f'"{data}"'
        return data

    @abstractmethod
    def connect(self, func:Callable[Any, [Union[pd.DataFrame, Tuple[tuple], None]]], **kwargs) -> Union[pd.DataFrame, Tuple[tuple], None]:
        """Create a connection to the database, and close it after excuting ``func`` .

        Args:
            func (Callable[Any, [Union[pd.DataFrame, Tuple[tuple], None]]]) : The function you want to execute. Receive ``cursor`` as the first argument.

        Returns:
            Union[pd.DataFrame, Tuple[tuple], None]: Return value from ``func``
        """
        check_environ(
            required_keynames=self.required_keynames,
            required_env_varnames=self.required_env_varnames,
            # database=database,
        )
        connection = "Create a connection to the database." # XXX.connect(
        #     database=self.get_val("database", database=database),
        # )
        cursor = connection.cursor()
        ret = func# (cursor=XXX_cursor, **kwargs)
        cursor.close()
        connection.commit()
        connection.close()
        return ret

    def execute(self, query:str, columns:List[str]=[], verbose:bool=False) -> Union[pd.DataFrame, Tuple[tuple], None]:
        """Execute a SQL query.

        Args:
            query (str)                   : Query to execute on server.
            columns (List[str], optional) : If this value is fiven, Return value will be as a ``pd.DataFrame`` format. Defaults to ``[]``.
            verbose (bool, optional)      : Whether to display the query or not. Defaults to ``False``.

        Returns:
            Union[pd.DataFrame, Tuple[tuple], None]: Return value of query.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> sql.execute("show databases;")
                (('information_schema',),
                 ('mysql',),
                 ('performance_schema',),
                 ('remody',),
                 ('sys',))
            >>> # Receive as a DataFrame.
            >>> df = sql.execute("show databases;", columns=["name"])
            >>> print(df.to_markdown())
                |    | name               |
                |---:|:-------------------|
                |  0 | information_schema |
                |  1 | mysql              |
                |  2 | performance_schema |
                |  3 | remody             |
                |  4 | sys                |
        """
        if verbose: print(query)
        def execute_query(cursor:Any) -> Tuple[tuple]:
            """Execute a query and

            Args:
                cursor (Any) : Database cursor to use.

            Returns:
                Tuple[tuple]: Return value of ``query``.
            """
            cursor.execute(query)
            return cursor.fetchall()
        ret = self.connect(func=execute_query)
        if len(columns)>0:
            ret = pd.DataFrame(data=ret, columns=columns)
        return ret

    def create(self, table:str, verbose:bool=False, column_info={}) -> None:
        """Create a Table named ``table`` .

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.
            columninfo (dict)        : Key value style column information.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> sql.create(table="pycharmers_user", column_info={
            ...     "id"      : 'int NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT "ID"',
            ...     "username": 'VARCHAR(100) NOT NULL COMMENT "ユーザー名"',
            ...     "created" : 'datetime DEFAULT NULL COMMENT "登録日"' ,
            >>> })
        """
        return self.execute(f"CREATE TABLE {table} ({','.join([f'`{k}` {v}' for k,v in column_info.items()])});", verbose=verbose)

    def drop(self, table:str, verbose:bool=False) -> None:
        """Drop the ``table`` .

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> sql.drop(table="pycharmers_user")
        """
        return self.execute(f"DROP TABLE {table};", verbose=verbose)

    def describe(self, table:str, verbose:bool=False) -> pd.DataFrame:
        """Get table structure.

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Table structure.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> df = sql.describe(table="pycharmers_user")
            >>> print(df.to_markdown())
            |    | Field    | Type         | Null   | Key   | Default   | Extra          |
            |---:|:---------|:-------------|:-------|:------|:----------|:---------------|
            |  0 | id       | int(11)      | NO     | PRI   |           | auto_increment |
            |  1 | username | varchar(100) | NO     |       |           |                |
            |  2 | created  | datetime     | YES    |       |           |                |
        """
        return self.execute(f"DESCRIBE {table};", columns=["Field","Type","Null","Key","Default","Extra"], verbose=verbose)

    def insert(self, table:str, data:List[list], columns:list=[], col_type="input_field", verbose:bool=False) -> int:
        """Insert a record to specified ``table``

        Args:
            table (str)              : The name of the table.
            data (List[list])        : Data to be inserted.
            columns (list, optional) : Column names to be inserted values. Defaults to ``[]``.
            col_type (str, optional) : If ``columns`` has no data, use :meth:`get_colnames <pycharmers.sdk.mysql.PycharmersSQL.get_colnames>` to decide which columns to be inseted. Defaults to ``"input_field"``.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            int: The number of rows in ``table``

        Examples:
            >>> import datetime
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> sql.insert(table="pycharmers_user", data=[
            ...     ["iwasaki", "now()"],
            ...     ["shuto", datetime.datetime(1998,7,3)]
            >>> ], columns=["username", "created"])
        """
        if len(columns)==0:
            columns = self.get_colnames(table=table, col_type=col_type)
        if not isinstance(data[0], list):
            data = [data]
        df_field = self.describe(table=table)
        coltypes = df_field.set_index("Field").filter(items=columns, axis=0).Type
        values = ", ".join([f"({', '.join([self.format_data(e,t) for e,t in zip(d,coltypes)])})" for d in data])
        return self.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES {values}", verbose=verbose)

    def update(self, table:str, old_column:str, old_value:Any, new_columns:List[str], new_values:List[Any], verbose:bool=False) -> None:
        """Update records.

        Args:
            table (str)              : The name of table.
            old_column (str)         : [description]
            old_value (Any)          :
            new_columns (List[str])  : [description]
            new_values (List[Any])   :
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> print(sql.selectAll(table="pycharmers_user").to_markdown())
                |    |   id | username   | created             |
                |---:|-----:|:-----------|:--------------------|
                |  0 |    1 | iwasaki    | 2021-05-22 07:23:10 |
                |  1 |    2 | shuto      | 1998-07-03 00:00:00 |
            >>> sql.update(table="pycharmers_user", old_column="username", old_value="iwasaki", new_column="created", new_value="now()")
            >>> print(sql.selectAll(table="pycharmers_user").to_markdown())
                |    |   id | username   | created             |
                |---:|-----:|:-----------|:--------------------|
                |  0 |    1 | iwasaki    | 2021-05-22 07:28:09 |
                |  1 |    2 | shuto      | 1998-07-03 00:00:00 |
        """
        df_field = self.describe(table=table)
        old_type = df_field[df_field.Field==old_column].Type.values[0]
        new_coltypes = df_field.set_index("Field").filter(items=new_columns, axis=0).Type
        update_values = ", ".join([f"{col} = {self.format_data(val, type)}" for col,val,type in zip(new_columns, new_values, new_coltypes)])
        return self.execute(f"UPDATE {table} SET {update_values} WHERE {old_column} = {self.format_data(old_value, old_type)}", verbose=verbose)

    def delete(self, table:str, column:str, value:Any, verbose:bool=False) -> None:
        """Delete the records whose ``column`` is ``value`` from the table named ``table`` .

        Args:
            table (str)              : The name of table.
            column (str)             :
            value (Any)              :
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> print(sql.select(table="pycharmers_user").to_markdown())
                |    |   id | username   | created             |
                |---:|-----:|:-----------|:--------------------|
                |  0 |    1 | iwasaki    | 2021-05-22 07:23:10 |
                |  1 |    2 | shuto      | 1998-07-03 00:00:00 |
            >>> sql.delete(table="pycharmers_user", column="username", value="shuto")
            >>> print(sql.select(table="pycharmers_user").to_markdown())
                |    |   id | username   | created             |
                |---:|-----:|:-----------|:--------------------|
                |  0 |    1 | iwasaki    | 2021-05-22 07:23:10 |
        """
        df_field = self.describe(table=table)
        type = df_field[df_field.Field==column].Type.values[0]
        return self.execute(f"DELETE FROM {table} WHERE {column} = {self.format_data(value, type)}", verbose=verbose)

    def merge(self, table1info:Dict[str,List[str]], table2info:Dict[str,List[str]], method:str="inner", verbose:bool=False) -> pd.DataFrame:
        """Select values from table1 and table2 using ``method`` JOIN

        Args:
            table1info (Dict[str,List[str]]) : Table1 information ( ``key`` : table name, ``value`` : selected columns (0th column is used for merging.))
            table2info (Dict[str,List[str]]) : Table2 information ( ``key`` : table name, ``value`` : selected columns (0th column is used for merging.))
            method (str, optional)           : How to merge two tables. Defaults to ``"inner"``.
            verbose (bool, optional)         : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Merged table records.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql.merge(
            ...     table1info={"user": ["id", "name", "job_id"]},
            ...     table2info={"jobs": ["id", "job_name"]},
            ...     method="inner", verbose=True
            >>> )
            >>> SELECT user.name, user.job_id, jobs.job_name FROM user INNER JOIN jobs ON user.id = jobs.id;
        """
        table1,columns1 = table1info.popitem()
        table2,columns2 = table2info.popitem()
        col_merge1 = columns1.pop(0)
        col_merge2 = columns2.pop(0)
        return self.execute(f"SELECT {', '.join([f'{table1}.{col}' for col in columns1] + [f'{table2}.{col}' for col in columns2])} FROM {table1} {method.upper()} JOIN {table2} ON {table1}.{col_merge1} = {table2}.{col_merge2};", columns=columns1+columns2, verbose=verbose)

    def get_colnames(self, table:str, col_type:str="all") -> list:
        """Get column names in the specified ``table`` .

        Args:
            table (str)              : The name of table.
            col_type (str, optional) : What types columns to extract. Defaults to ``"all"``.

        Returns:
            list: Extracted Columns.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> sql.get_colnames(table="pycharmers_user")
            >>> ['id', 'username', 'created']
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

    def select(self, table:str, columns:List[str]=[], where:Dict[str,Any]={}, verbose:bool=False) -> pd.DataFrame:
        """Get selected records.

        Args:
            table (str)                     : The name of table.
            columns (List[str], optional)   : Selected Columns. If you don't specify any columns, extract all columns. Defaults to ``[]``.
            where (Dict[str,Any], optional) : Specify the condition of the column to be extracted. { ``colname`` : ``value`` }
            verbose (bool, optional)        : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Selected Records.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> df = sql.select(table="pycharmers_user")
            >>> print(df.to_markdown())
                |    |   id | username   | created             |
                |---:|-----:|:-----------|:--------------------|
                |  0 |    1 | iwasaki    | 2021-05-22 07:23:10 |
                |  1 |    2 | shuto      | 1998-07-03 00:00:00 |
            >>> df = sql.select(table="pycharmers_user", columns=["id", "username"])
            >>> print(df.to_markdown())
                |    |   id | username   |
                |---:|-----:|:-----------|
                |  0 |    1 | iwasaki    |
                |  1 |    2 | shuto      |
        """
        if len(columns)==0:
            columns = self.get_colnames(table=table, col_type="all")
        if len(where)>0:
            df_field = self.describe(table=table)
            coltypes = df_field.set_index("Field").filter(items=list(where.keys()), axis=0).Type
            WHERE = f'WHERE {" AND ".join([f"{key} = {self.format_data(val,type)}" for type,(key,val) in zip(coltypes,where.items())])}'
        else:
            WHERE = ""
        return self.execute(f"SELECT {', '.join(columns)} FROM {table} {WHERE};", columns=columns, verbose=verbose)

    def count_rows(self, table:str, verbose:bool=False) -> int:
        """Get the number of rows in the ``table`` .

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            int: The number of rows in the specified ``table`` .

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> sql.count_rows(table="pycharmers_user")
                2
        """
        return self.execute(f"SELECT count(*) FROM {table};")[0][0]

    def show_tables(self, verbose:bool=False) -> pd.DataFrame:
        """Show all tables.

        Args:
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Information for all Tables.

        >>> from pycharmers.sdk import PycharmersSQL
        >>> sql = PycharmersSQL()
        >>> df = sql.show_tables()
        >>> print(df.to_markdown())
            |    | Name            | Engine   |   Version | Row_format   |   Rows |   Avg_row_length |   Data_length |   Max_data_length |   Index_length |   Data_free |   Auto_increment | Create_time         | Update_time         | Check_time   | Collation       | Checksum   | Create_options   | Comment   |
            |---:|:----------------|:---------|----------:|:-------------|-------:|-----------------:|--------------:|------------------:|---------------:|------------:|-----------------:|:--------------------|:--------------------|:-------------|:----------------|:-----------|:-----------------|:----------|
            |  0 | pycharmers_user | InnoDB   |        10 | Dynamic      |      0 |                0 |         16384 |                 0 |              0 |           0 |                1 | 2021-05-22 07:06:17 | NaT                 |              | utf8_general_ci |            |                  |           |
        """
        return self.execute("show table status;", columns=['Name', 'Engine', 'Version', 'Row_format', 'Rows', 'Avg_row_length', 'Data_length', 'Max_data_length', 'Index_length', 'Data_free', 'Auto_increment', 'Create_time', 'Update_time', 'Check_time', 'Collation', 'Checksum', 'Create_options', 'Comment'], verbose=verbose)

    def explain(self, table:str, verbose:bool=False) -> pd.DataFrame:
        """Explain records

        Args:
            table (str)              : The name of table.
            verbose (bool, optional) : Whether to display the query or not. Defaults to ``False``.

        Returns:
            pd.DataFrame: Explanation for records.

        Examples:
            >>> from pycharmers.sdk import PycharmersSQL
            >>> sql = PycharmersSQL()
            >>> df = sql.explain(table="pycharmers_user")
            >>> print(df.to_markdown())
            |    |   id | select_type   | table           | partition   | type   | possible_keys   | key   | key_len   | ref   |   rows |   filtered | Extra   |
            |---:|-----:|:--------------|:----------------|:------------|:-------|:----------------|:------|:----------|:------|-------:|-----------:|:--------|
            |  0 |    1 | SIMPLE        | pycharmers_user |             | ALL    |                 |       |           |       |      2 |        100 |         |
        """
        return self.execute(f"EXPLAIN SELECT * FROM {table};", columns=["id","select_type","table","partition","type","possible_keys","key","key_len","ref","rows","filtered","Extra"], verbose=verbose)
