"""A Wrapper class for GoogleDrive in `PyDrive <https://pythonhosted.org/PyDrive/index.html>`_"""
#coding: utf-8
import os
import re
from ..utils import tabulate
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class PyCharmersGoogleDrive(GoogleDrive):
    """Wrapper class for GoogleDrive.

    Args:
        settings_file (str) : path of settings file. Defaults to ``'settings.yaml'`` .
        http_timeout (int)  : HTTP timeout. Defaults to None.

    Examples:
        >>> from pycharmers.api import PyCharmersGoogleDrive
        >>> drive = PyCharmersGoogleDrive(settings_file='dir/subdir/settings.yaml')
        >>> drive

    When executed as above, the directory structure is as follows.

    .. code-block:: shell

        $ tree .
        .
        └── dir
            └── subdir
                ├── client_secrets.json
                ├── credentials.json
                └── settings.yaml

    ``settings.yaml`` is like `this <https://pythonhosted.org/PyDrive/oauth.html?highlight=yaml#sample-settings-yaml>`_ .

    .. code-block:: yaml

        client_config_backend: settings
        client_config:
            client_id: <CLIENT_ID>
            client_secret: <CLIENT_SECRET
        save_credentials: True
        save_credentials_backend: file
        save_credentials_file: credentials.json
        get_refresh_token: True
        oauth_scope:
            - https://www.googleapis.com/auth/drive.file
            - https://www.googleapis.com/auth/drive.install
            - https://www.googleapis.com/auth/drive
    """
    def __init__(self, settings_file='settings.yaml', http_timeout=None):
        self.auth = self.authenticate(settings_file=settings_file, http_timeout=http_timeout)
        super().__init__(auth=self.auth)

    @staticmethod
    def authenticate(settings_file='settings.yaml', http_timeout=None):
        """Get an Authentication. See the `PyDrive's documentation <https://pythonhosted.org/PyDrive/oauth.html?highlight=yaml#sample-settings-yaml>`_

        Args:
            settings_file (str) : path of settings file. Defaults to ``'settings.yaml'`` .
            http_timeout (int)  : HTTP timeout. Defaults to None.

        Returns:
            GoogleAuth: Wrapper class for oauth2client library in google-api-python-client.
        """
        dirname, filename = os.path.split(settings_file)
        cwd = os.getcwd()
        # Change directory to where settings_file exists.
        os.chdir(dirname)
        gauth = GoogleAuth(settings_file=filename)
        gauth.LocalWebserverAuth()
        # Back to the original directory.
        os.chdir(cwd)
        return gauth

    @staticmethod
    def arrange_queries(queries=[], ext=None, isfile=None, trashed=False):
        """Arrange queries for ``Files.List()``

        Args:
            queries (list)  : Current queries. Defaults to [].
            only_mp4 (bool) : Whether to extract only ``.mp4`` (zoom). Defaults to True.
            minetypes (str) : If ``minetypes``[description]. Defaults to "file".

        Returns:
            dict: parameter to be sent to ``Files.List()`` .

        Examples:
            >>> from pycharmers.api import PyCharmersGoogleDrive
            >>> PyCharmersGoogleDrive.arrange_queries(queries=[], ext=".mp4", isfile=True, trashed=False)
            {'q': 'title contains ".mp4" and mimeType != "application/vnd.google-apps.folder" and trashed = false'}
            >>> PyCharmersGoogleDrive.arrange_queries(queries=[], ext=None, isfile=False, trashed=None)
            {'q': 'mimeType  = "application/vnd.google-apps.folder" and trashed = none'}            
        """
        if ext is not None:
            queries.append(QUERY.TITLE_CONTAIN.format(q=ext))
        if isfile is not None:
            if isfile:
                queries.append(QUERY.FILES)
            else:
                queries.append(QUERY.FOLDERS)
        queries.append(QUERY.TRASHED.format(q=str(trashed).lower()))
        return {"q": " and ".join(queries)}

    def getListFile(self, param=None):
        """Create an instance of GoogleDriveFileList with auth of this instance.

        Args:
            param (dict) : parameter to be sent to ``Files.List()`` .

        Returns:
            GoogleDriveFileList: Google Drive File List.
        """
        return self.ListFile(param=param).GetList()

    def get_file_list(self, dirname=None, dirId="root", ext=None, isfile=None):
        """Use queries effortlessly to get a list of files.

        Args:
            dirname (str) : Directory Name. Defaults to None.
            dirId (str)   : Directory Id
            ext (str)     : File Extensions.
            isfile (bool) : If this value is ``True``, extract only "file", else if this value is ``False``, extract only "folder", else (if this value is ``None`` ) extract "both".

        Returns:
            GoogleDriveFileList: Google Drive File List.

        Examples:
            >>> from pycharmers.api import PyCharmersGoogleDrive
            >>> drive = PyCharmersGoogleDrive(settings_file="settings.json")
            >>> for f in drive.get_file_list(dirname="DIRNAME"):
            ...     print(f["title"], f["id"])
        """
        if dirname is not None:
            directory = self.getListFile(param={'q': QUERY.TITLE_MATCH.format(q=dirname)})
            if len(directory)>0:
                dirId = directory[0]["id"]
            else:
                print(f"{dirname} is not found.")
        return self.getListFile(param=self.arrange_queries(queries=[QUERY.PARENT.format(q=dirId)], ext=ext, isfile=isfile))

class QUERY:
    """Query to be sent to ``Files.List()`` .
    
    +------------------------------+---------------------------------------------------------+
    |          References          |                           URL                           |
    +==============================+=========================================================+
    |          Japanese cheatsheet |          https://note.nkmk.me/python-pydrive-list-file/ |
    +------------------------------+---------------------------------------------------------+
    |     Commonly Used MIME Types | https://learndataanalysis.org/commonly-used-mime-types/ |
    +------------------------------+---------------------------------------------------------+
    | G Suite and Drive MIME Types |   https://developers.google.com/drive/api/v3/mime-types |
    +------------------------------+---------------------------------------------------------+
    """
    FOLDERS       = 'mimeType  = "application/vnd.google-apps.folder"'
    FILES         = 'mimeType != "application/vnd.google-apps.folder"'
    TITLE_MATCH   = 'title = "{q}"'
    TITLE_CONTAIN = 'title contains "{q}"'
    PARENT        = '"{q}" in parents'
    TRASHED       = 'trashed = {q}'
    
    def show():
        """Show all Queries.

        Examples:
            >>> from pycharmers.api.google_drive import QUERY
            >>> QUERY.show()
        """
        tabulate(tabular_data=[[k,v] for k,v in QUERY.__dict__.items() if re.match(pattern=r"[A-Z]+", string=k)], headers=["NAME", "query"])
