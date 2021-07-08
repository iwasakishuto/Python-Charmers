#coding: utf-8
import pandas as pd
import datetime
import sqlite3
from typing import Any,Optional,Callable,Union,List,Tuple,Dict

from ..utils._colorings import toBLUE, toGREEN, toRED
from ..utils.environ_utils import check_environ
from ..utils.generic_utils import handleKeyError
from .base import PycharmersSQL

class PycharmersSQLite(PycharmersSQL):
    """Wrapper class for Sqlite.

    Args:
        database (Optional[str], optional) : database to use. Defaults to ``None``.
        verbose (bool, optional)           : Whether to print message or not Defaults to ``False``.
    """
    def __init__(self, database:Optional[str]=None, verbose:bool=False):
        super().__init__(
            api_name="SQLite",
            verbose=verbose,
            database=database,
        )

    def connect(self, func:Callable, database:Optional[str]=None, **kwargs) -> Union[pd.DataFrame, Tuple[tuple], None]:
        """Use ``MySQLdb.connect`` to create a connection to the database, and close it after excuting ``func`` .

        Args:
            func (Callable)                    : The function you want to execute. Receive ``cursor`` as the first argument.
            database (Optional[str], optional) : database to ues. Defaults to ``None``.
            kwargs (dict)                      : See a table below.

        Returns:
            Any: Return value of ``func``
        """
        check_environ(
            required_keynames=self.required_keynames,
            required_env_varnames=self.required_env_varnames,
            database=database,
        )
        connection = sqlite3.connect(database=self.get_val("database", database=database))
        cursor = connection.cursor()
        ret = func(cursor=cursor, **kwargs)
        cursor.close()
        connection.commit()
        connection.close()
        return ret