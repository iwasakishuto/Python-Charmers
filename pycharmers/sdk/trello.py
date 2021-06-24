"""A wrapper class for `Trello API <https://developer.atlassian.com/cloud/trello/>`_"""
#coding: utf-8
import json
import requests

from ..utils._path import DOTENV_PATH
from ..utils.environ_utils import name2envname, check_environ
from ..utils.json_utils import dumps_json
from ..utils.print_utils import tabulate
from ._base import PycharmersSDK

class Trello(PycharmersSDK):
    """A wrapper class for `Trello API <https://developer.atlassian.com/cloud/trello/>`_

    Visit https://trello.com/app-key to get an API key and Token. (NOTE: You have to login before visiting)

    Args:
        api_key (str)  : API-key.
        token (str)    : Token.
        verbose (bool) : Whether to print logs or not. 

    """
    def __init__(self, apikey=None, token=None, verbose=True):
        super().__init__(
            api_name="Trello", 
            verbose=verbose,
            apikey=apikey, token=token,
        )
        self.setup_show_func()

    def api_call(self, url, apikey=None, token=None):
        """Get information about the memberships users have to the board.

        Args:
            url (str)      : URL to which the API sends the request.
            api_key (str)  : API-key.
            token (str)    : Token.
        """
        check_environ(
            required_keynames=self.required_keynames, 
            required_env_varnames=self.required_env_varnames,
            apikey=apikey,
            token=token,
        )
        response = requests.get(
            url=url,
            headers = {
                "Accept": "application/json",
            },
            params={
                "key"   : self.get_val("apikey", apikey=apikey),
                "token" : self.get_val("token", token=token), 
            },
        )
        return json.loads(response.text)

    @staticmethod
    def show_results(result, keynames=["name", "id"]):
        """Static Method for displaying result beautifullly.
        
        Args:
            result (list)   : Result.
            keynames (list) : The keyname to extract and display the value from the ``result``

        Examples:
            >>> from pycharmers.sdk import Trello
            >>> Trello.show_results(result=[
            ...     {"api": "slack",  "foo": 1, "bar": ["get"]},
            ...     {"api": "github", "foo": 2, "bar": ["post"]}
            >>> ], keynames=["api", "b"])
            +--------+------+
            |  api   |  b   |
            +========+======+
            |  slack | None |
            +--------+------+
            | github | None |
            +--------+------+
        """
        tabulate(tabular_data=[[e.get(c) for c in keynames] for e in result], headers=keynames)

    def setup_show_func(self):
        """Set up the ``show_XXX`` funciton."""
        method2showkeynames = {
            "memberships_of_a_board" : ["name", "id", "url"],
            "lists_on_a_board"       : ["name", "id"],
            "cards_on_a_board"       : ["name", "id", "idList"],
            "cards_in_a_list"        : ["name", "id"],
        }
        for method_name, default_keynames in method2showkeynames.items():
            def show_func(*args, keynames=default_keynames, method_name=method_name, **kwargs):
                get_func = getattr(self, f"get_{method_name}")
                self.show_results(result=get_func(*args, **kwargs), keynames=keynames)
            show_func.__doc__ = f"See :meth:`get_{method_name} <pycharmers.sdk.trello.get_{method_name}>` for the required arguments."
            setattr(self, f"show_{method_name}", show_func)

    def get_memberships_of_a_board(self, username=None, apikey=None, token=None):
        """API wrapper for `Get Memberships of a Board <https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-memberships-get>`_"""
        return self.api_call(url=f"https://api.trello.com/1/members/{username}/boards", apikey=apikey, token=token)

    def get_lists_on_a_board(self, board_id, apikey=None, token=None):
        """API wrapper for `Get Lists on a Board <https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get>`_"""
        return self.api_call(url=f"https://api.trello.com/1/boards/{board_id}/lists", apikey=apikey, token=token)

    def get_cards_on_a_board(self, board_id, apikey=None, token=None):
        """API wrapper for `Get Cards on a Board <https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get>`_"""
        return self.api_call(url=f"https://api.trello.com/1/boards/{board_id}/cards", apikey=apikey, token=token)

    def get_cards_in_a_list(self, board_id, apikey=None, token=None):
        """API wrapper for `Get Cards in a List <https://developer.atlassian.com/cloud/trello/rest/api-group-lists/#api-lists-id-cards-get>`_"""
        return self.api_call(url=f"https://api.trello.com/1/lists/{board_id}/cards", apikey=apikey, token=token)
