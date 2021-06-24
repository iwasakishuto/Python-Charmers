"""A Wrapper class for GoogleDrive in `PyDrive <https://pythonhosted.org/PyDrive/index.html>`_"""
#coding: utf-8
import os
import re
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from ..utils.print_utils import tabulate
from ..utils._colorings import toBLUE, toGREEN, toRED

class PyCharmersGoogleDrive(GoogleDrive):
    """Wrapper class for GoogleDrive.

    Args:
        settings_file (str) : path of settings file. Defaults to ``'settings.yaml'`` .
        http_timeout (int)  : HTTP timeout. Defaults to None.

    Examples:
        >>> from pycharmers.sdk import PyCharmersGoogleDrive
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
        self.dirId2name = {}

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
        if dirname!="": os.chdir(dirname)
        gauth = GoogleAuth(settings_file=filename)
        gauth.LocalWebserverAuth()
        # Back to the original directory.
        os.chdir(cwd)
        return gauth

    @staticmethod
    def arrange_queries(queries=[], ext=None, isfile=None, trashed=False, verbose=False):
        """Arrange queries for ``Files.List()``

        Args:
            queries (list) : Current queries. Defaults to ``[]`` .
            ext (str)      : File Extensions. Defaults to ``None`` .
            isfile (bool)  : If this value is ``True``, extract only "file", else if this value is ``False``, extract only "folder", else (if this value is ``None`` ) extract "both".
            trashed (bool) : Whether trashed file or not. Defaults to ``False``
            verbose (bool) : Whether to print the query or not. Defaults to ``False``

        Returns:
            dict: parameter to be sent to ``Files.List()`` .

        Examples:
            >>> from pycharmers.sdk import PyCharmersGoogleDrive
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
        if verbose:
            print("[Queries]")
            for q in queries:
                print(f"* {q}")
        return {"q": " and ".join(queries)}

    def getListFile(self, param=None):
        """Create an instance of GoogleDriveFileList with auth of this instance.

        Args:
            param (dict) : parameter to be sent to ``Files.List()`` .

        Returns:
            GoogleDriveFileList: Google Drive File List.
        """
        return self.ListFile(param=param).GetList()

    def get_file_list(self, filename=None, dirname=None, dirId="root", ext=None, isfile=None, trashed=False, recursive=False, verbose=False):
        """Use queries effortlessly to get a list of files.

        Args:
            filename (str)   : Exact File Name. Defaults to ``None`` .
            dirname (str)    : Directory Name. Defaults to ``None`` .
            dirId (str)      : Directory Id. Defaults to ``None`` .
            ext (str)        : File Extensions. Defaults to ``None`` .
            isfile (bool)    : If this value is ``True``, extract only "file", else if this value is ``False``, extract only "folder", else (if this value is ``None`` ) extract "both".
            trashed (bool)   : Whether trashed file or not. Defaults to ``False``
            recursive (bool) : Whether to find files recursively. Defaults to ``False`` 
            verbose (bool)   : Whether to print the query or not. Defaults to ``False``

        Returns:
            GoogleDriveFileList: Google Drive File List.

        Examples:
            >>> from pycharmers.sdk import PyCharmersGoogleDrive
            >>> drive = PyCharmersGoogleDrive(settings_file="settings.json")
            >>> for f in drive.get_file_list(dirname="DIRNAME"):
            ...     print(f["title"], f["id"])
        """
        queries = [QUERY.PARENT.format(q=self.get_dirId(dirname=dirname, dirId=dirId))]
        if filename is not None:
            queries.append(QUERY.TITLE_MATCH.format(q=filename))
        fileLists = self.getListFile(param=self.arrange_queries(queries=queries, ext=ext, isfile=isfile, trashed=trashed, verbose=verbose))
        if recursive:
            for f in self.getListFile(param=self.arrange_queries(queries=queries[:1], isfile=False, trashed=trashed, verbose=verbose)):
                fileLists.extend(self.get_file_list(filename=filename, dirname=None, dirId=f["id"], ext=ext, isfile=isfile, trashed=trashed, recursive=recursive, verbose=verbose))
        return fileLists

    def get_dirId(self, dirname=None, dirId="root"):
        """Get directory Id.

        Args:
            dirname (str) : Directory Name. Defaults to ``None`` .
            dirId (str)   : Directory Id. Defaults to ``"root"`` .

        Returns:
            str : Directory Id.
        """
        if dirname is not None:
            directory = self.getListFile(param={'q': QUERY.TITLE_MATCH.format(q=dirname)})
            if len(directory)>0:
                dirId = directory[0]["id"]
            else:
                print(f"Folder {toBLUE(dirname)} is not found in your GoogleDrive. Try to specify the {toGREEN('dirId')}")
        return dirId

    def upload(self, filepath, verbose=True):
        """Upload file.

        Args:
            filepath (str): name of the file to be uploaded.

        Returns:
            GoogleDriveFile: Google Drive File Info.
        """
        file = self.CreateFile()
        file.SetContentFile(filename=filepath)
        file["title"] = os.path.basename(filepath)
        file.Upload()
        if verbose:
            print(f"{toGREEN('[success]')} Upload {toBLUE(filepath)} (ID={toGREEN(file['id'])})")
        return file

    def download_file(self, filename=None, dirname=None, dirId="root", ext=None, isfile=None, trashed=False, dst=None, mimetype=None, remove_bom=False, verbose=True):
        """Download file.

        Args:
            filename (str)    : File Name. Defaults to ``None`` .
            dirname (str)     : Directory Name. Defaults to ``None`` .
            dirId (str)       : Directory Id. Defaults to ``None`` .
            ext (str)         : File Extensions. Defaults to ``None`` .
            isfile (bool)     : If this value is ``True``, extract only "file", else if this value is ``False``, extract only "folder", else (if this value is ``None`` ) extract "both".
            trashed (bool)    : Whether trashed file or not. Defaults to ``False``
            dst (str)         : Where to download the file. Defaults to ``None`` .
            mimetype (str)    : mimeType of the file.. Defaults to ``None`` .
            remove_bom (bool) : Whether to remove the byte order marking.. Defaults to ``False``.
            verbose (bool)    : Whether to print the result or not. Defaults to ``True``

        Returns:
            str : Path to downloaded file.

        Examples:
            >>> from pycharmers.sdk import PyCharmersGoogleDrive
            >>> drive = PyCharmersGoogleDrive(settings_file="settings.json")
            >>> drive.download_file(filename="file.png", dirId="root", verbose=True)
        """
        filelist = self.get_file_list(filename=filename, dirname=dirname, dirId=dirId, ext=ext, isfile=isfile, trashed=trashed, verbose=False)
        if len(filelist)>0:
            f = filelist[0]
            filename = f["title"]
            file = self.CreateFile({"id": f["id"]})
            dst = dst or filename
            file.GetContentFile(filename=dst, mimetype=mimetype, remove_bom=remove_bom)
        if verbose:
            print(f"{toGREEN('[success]') if len(filelist)>0 else toRED('[failure]')} Downloaded {toGREEN(filename)} to {toBLUE(dst)}")
        return dst

    def tree(self, dirname=None, dirId="root"):
        """list contents of directories in a tree-like format.

        Args:
            dirname (str) : Directory Name. Defaults to ``None`` .
            dirId (str)   : Directory Id. Defaults to ``"root"`` .

        TODO: To display the file contents in a tree-like format.

        Examples:
            >>> from pycharmers.sdk import PyCharmersGoogleDrive
            >>> drive = PyCharmersGoogleDrive(settings_file="settings.json")
            >>> drive.tree()
        """
        root_file_list = self.get_file_list(dirname=None, dirId="root")
        for f in root_file_list:
            p = f["parents"]
            if len(p)>0:
                self.dirId2name[p[0]["id"]] = "."
                self.dirId2name["root/"] = "./"
                break

        def dirId2name(f):
            for o,n in self.dirId2name.items():
                f = f.replace(o,n)
            return f

        for f in sorted(set([dirId2name(f) for f in self.tree_recursive(dirname=dirname, dirId=dirId, parents=[])])):
            print(f)

    def tree_recursive(self, dirname=None, dirId="root", parents=[]):
        """[summary]

        Args:
            dirname (str)  : Directory Name. Defaults to ``None`` .
            dirId (str)    : Directory Id. Defaults to ``"root"`` .
            parents (list) : Parent Directories. Defaults to ``[]``.

        Returns:
            list: All filepaths from initial ``dirname`` ( ``dirId`` )
        """
        filepaths = []
        dirId = self.get_dirId(dirname=dirname, dirId=dirId)
        if len(parents)==0:
            parents = [dirId]
        for f in self.get_file_list(dirname=None, dirId=dirId):
            title     = f["title"]
            is_folder = f["mimeType"]=='application/vnd.google-apps.folder'
            if len(f["parents"])>0:
                fp = "/".join(parents[:-1] + [p["id"] for p in reversed(f["parents"])] + [title]) 
            else:
                fp = f"shared/{title}"
            filepaths.append(fp)
            if is_folder:
                self.dirId2name[f["id"]] = f["title"]
                filepaths.extend(self.tree_recursive(dirname=None, dirId=f["id"], parents=parents+[f["id"]]))
        return filepaths

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
    
    @staticmethod
    def show():
        """Show all Queries.

        Examples:
            >>> from pycharmers.sdk.google_drive import QUERY
            >>> QUERY.show()
        """
        tabulate(tabular_data=[[k,v] for k,v in QUERY.__dict__.items() if re.match(pattern=r"[A-Z]+", string=k)], headers=["NAME", "query"])
