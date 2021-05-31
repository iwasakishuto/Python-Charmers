#coding: utf-8
import scp
import paramiko
from typing import Union,List,Tuple,Optional

class RemodySSHClient():
    """SSH Client for Remody Video Analysis Server."""
    def __init__(self, hostname:str, username:str, password:str, port:int=22):
        self.hostname = hostname
        self.port     = port
        self.username = username
        self.password = password

    def connect(self) -> paramiko.SSHClient:
        """Create a Connection to 

        Returns:
            paramiko.SSHClient: A high-level representation of a session with an SSH server.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
        return ssh

    @property
    def connection(self):
        return self.connect()

    def exec_command(self, command:str, bufsize:int=-1, timeout:Optional[int]=None, get_pty:bool=False, environment:Optional[dict]=None) -> Tuple[str,str,str]:
        """Execute a command on the SSH server.

        Args:
            command (str)                          : The command to execute.
            bufsize (int, optional)                : Interpreted the same way as by the built-in ``file()`` function in Python. Defaults to ``-1``.
            timeout (Optional[int], optional)      : Set command's channel timeout.. Defaults to ``None``.
            get_pty (bool, optional)               : Request a pseudo-terminal from the server. Defaults to ``False``.
            environment (Optional[dict], optional) : A dict of shell environment variables, to be merged into the default environment that the remote command executes within.. Defaults to ``None``.

        Returns:
            Tuple[str,str,str]: the stdin, stdout, and stderr of the executing command, as a 3-tuple.
        """

        with self.connection as sshc:
            stdin, stdout, stderr = sshc.exec_command(command=command, bufsize=bufsize, timeout=timeout, get_pty=get_pty, environment=environment)
        return (stdin, stdout, stderr)

    def scp_get(self, remote_path:str, local_path:str="", recursive:bool=True, preserve_times:bool=True):
        """Transfer files and directories from remote host to localhost.

        Args:
            remote_path (str)               : Path to retrieve from remote host. since this is evaluated by scp on the remote host, shell wildcards and environment variables may be used.
            local_path (str, optional)      : Path in which to receive files locally. Defaults to ``""``.
            recursive (bool, optional)      : Transfer files and directories recursively. Defaults to ``True``.
            preserve_times (bool, optional) : Preserve mtime and atime of transferred files and directories. Defaults to ``True``.
        """
        with scp.SCPClient(self.connection.get_transport()) as scpc:
            scpc.get(
                remote_path=remote_path,
                local_path=local_path,
                recursive=recursive,
                preserve_times=preserve_times,
            )

    def scp_put(self, files:Union[str,List[str]], remote_path:str=b".", recursive:bool=True, preserve_times:bool=True):
        """Transfer files and directories to remote host.

        Args:
            files (Union[str,List[str]])    : A single path, or a list of paths to be transferred. ``recursive`` must be ``True`` to transfer directories.
            remote_path (str, optional)     : spath in which to receive the files on the remote host. Defaults to ``b"."``.
            recursive (bool, optional)      : transfer files and directories recursively. Defaults to ``True``.
            preserve_times (bool, optional) : preserve mtime and atime of transferred files and directories. Defaults to ``True``.
        """
        with scp.SCPClient(self.connection.get_transport()) as scpc:
            scpc.put(
                files=files,
                remote_path=remote_path,
                recursive=recursive,
                preserve_times=preserve_times,
            )