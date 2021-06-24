# coding: utf-8
"""A Slack WebClient for `Using the Slack Web API <https://api.slack.com/web#basics>`_

This class is created by the following programs.

.. code-block:: python

    >>> import urllib
    >>> import pandas as pd
    >>> from pycharmers.utils import infer_types, get_soup, defFunction, render_template, html2reStructuredText, find_target_text
    ... 
    >>> def slack_method_create(url):
    ...    soup = get_soup(url)    
    ...    table = soup.find(name="table", class_="small full_width no_bottom_margin no_bottom_padding")
    ...    
    ...    tds = table.find_all(name="td")
    ...    api_method             = tds.pop(0).get_text().replace("https://slack.com/api/", ""); func_name = api_method.replace(".", "_")
    ...    http_method            = tds.pop(0).get_text()
    ...    accepted_content_types = tds.pop(0).get_text().split(", ")
    ...    
    ...    description=""
    ...    if len(tds)>1:
    ...        df = pd.read_html(str(tds[1].find(name="table")).replace("Â\\xa0 ", "``, ``"))[0]
    ...        df["Required scope(s)"] = df["Required scope(s)"].apply(lambda x: "``"+x+"``" ).apply(lambda x: x[:-6] if x[-6:] == ", ````" else x )
    ...        description = df.to_markdown(index=False, tablefmt="grid").replace("\\n", "\\n    ")
    ...    
    ...    def_func = defFunction(
    ...        func_name=func_name, 
    ...        short_description=find_target_text(soup=soup.find(name="section", class_="tab_pane selected clearfix large_bottom_padding"), name="p", default=""),
    ...        description=description,
    ...        is_method=True,
    ...    )
    ...    
    ...    for argument in soup.find(name="div", class_="method_arguments full_width").find_all(name="div", class_="method_argument")[1:]:
    ...        name = find_target_text(soup=argument, name="span", class_="arg_name")
    ...        if name=="team_id":
    ...            example = "T1234567890"
    ...        else:
    ...            example = argument.find(name="span", class_="arg_example")
    ...            if example != None:
    ...                example = example.find(name="code")
    ...                if example != None:
    ...                    example = example.text
    ...                    if len(example)>0:
    ...                        if example[0] in ["[", "{"]:
    ...                            example = { "first_name": "John" } if example == '{ first_name: "John", ... }' else eval(example)
    ...                        else:
    ...                            example = {
    ...                                "true" : True,
    ...                                "false" : False
    ...                            }.get(example, example)
    ...        type = infer_types(example)
    ...        if example is not None:
    ...            try:
    ...                example = type(example)
    ...            except:
    ...                pass
    ...        def_func.set_argument(
    ...            name=name,
    ...            type=type, 
    ...            is_required=find_target_text(soup=argument, name="span", class_="arg_requirement") == "Required", 
    ...            default=example,
    ...            example=example,
    ...            description=html2reStructuredText(
    ...                html=str(argument.find(name="p"))[3:-4], 
    ...                base_url=url
    ...            ).replace("below", "here").replace("false", "False").replace("true", "True").replace("none", "None")
    ...        )
    ...       
    ...    def_func.set_example(prefix="\\n".join([">>> import os", ">>> from pycharmers.sdk import SlackClient", '>>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])', ">>> res = client.{func_name}("]))
    ...    def_func.create()
    ...    
    ...    render_template(template_name_or_string='{%- from "_macros/utils.html" import pythonalization %}    params = locals()\\n    params.pop("self")\\n    self._api_wrapper(\\n        api_method={{ pythonalization(api_method) }}, \\n        http_method={{ pythonalization(http_method) }}, \\n        content_types={{ pythonalization(content_types) }},\\n        **params,        \\n    )', context={"api_method": api_method, "http_method": http_method, "content_types": accepted_content_types})
    ...    
    >>> url = "https://api.slack.com/methods"
    >>> soup = get_soup(url)
    >>> for i,aTag in enumerate(soup.find(name="div", class_="tab_pane selected").find_all(name="a")[1:-3]):
    ...     slack_method_create(url=urllib.parse.urljoin(base=url, url=aTag.get("href")))

"""
import io
import uuid
import sys
import json as js
import platform
import urllib
import mimetypes

from ..__meta__ import __version__, __module_name__
from ..utils import pretty_3quote, toBLUE, toGREEN

class SlackClient():
    """A Slack WebClient for `Using the Slack Web API <https://api.slack.com/web#basics>`_
    
    The Slack Web API is an interface for querying information from and enacting change in a Slack workspace.
    This client handles constructing and sending HTTP requests to Slack as well as receiving responses.

    Attributes:
        token (str)    : A string specifying an xoxp or xoxb token.
        base_url (str) : A string representing the Slack API base URL.(default= ``"https://www.slack.com/api/"``)
        header (dict)  : A header.
    """
    def __init__(self, token=None, timeout=30):
        self.base_url = "https://www.slack.com/api/"
        self.is_slack_token(token=token)
        self.timeout = timeout
        self.header = {
            "Content-Type"  : "application/x-www-form-urlencoded",
            "User-Agent"    : "Python/{pv.major}.{pv.minor}.{pv.micro} {mn}/{mv} {s}/{r}".format(pv=sys.version_info, mn=__module_name__, mv=__version__, s=platform.system(), r=platform.release()),
            "Authorization" : "Bearer {t}".format(t=self.token)
        }

    def is_slack_token(self, token=None):
        """Check whther given ``token`` is valid slack token or not, and set it to attribute.
        
        Args:
            token (str) : A string specifying an xoxp or xoxb token.

        Raises:
            ValueError : If token is not valid.
        """
        if (token is None) or (token[:4] not in ["xoxp", "xoxb"]):
            raise ValueError(*pretty_3quote(f"""
            Please create a token. (If you have already created, start from 5)
                1. Access {toBLUE("https://api.slack.com/apps")}.
                2. Click {toGREEN("[Create New App]")} to create your Slack App.
                3. Click {toGREEN("[Basic Information]")} -> {toGREEN("[Add features and functionality]")} -> {toGREEN("[Permissions]")} to set your desired Permission Scopes.
                4. Click {toGREEN("[Basic Information]")} -> {toGREEN("[Install your app]")} -> {toGREEN("[Install to Workspace]")} to install this App to your Workspace.
                5. Visit {toBLUE("https://api.slack.com/apps")} again.
                6. Click {toGREEN("[Basic Information]")} -> {toGREEN("[Add features and functionality]")} -> {toGREEN("[Permissions]")} and check {toGREEN("OAuth & Permissions")} to get {toGREEN("Bot User OAuth Access Token")} (xoxb-XXXX)
            """))
        self.token = token

    def _api_wrapper(self, api_method, http_method="POST", content_types=["application/x-www-form-urlencoded"], **params):
        """Wrapper for :meth:`api_call <pycharmers.sdk.slack.SlackClient.api_call>`."""
        for content_type in content_types:
            if content_type=="application/json;charset=utf-8":
                data = {"json": params}
            elif content_type=="application/x-www-form-urlencoded":
                data = {"params": params}
            elif content_type.startswith("multipart/form-data"):
                data = {"data": params}
            try:
                return self.api_call(
                    url=urllib.parse.urljoin(base=self.base_url, url=api_method),
                    http_method=http_method,
                    **data
                )
            except:
                pass

    def api_call(self, url, http_method="POST", files={}, data={}, params={}, json={}):
        """Constructs a request and executes the API call to Slack.

        Args:
            url (str)         : The target Slack API method.
            http_method (str) : HTTP Verb.(default= ``"POST"`` )
            data (dict)       : The body to attach to the request. If a dictionary is provided, form-encoding will take place. e.g. ``{'key1': 'value1', 'key2': 'value2'}``
            params (dict)     : The URL parameters to append to the URL. e.g. ``{'key1': 'value1', 'key2': 'value2'}``
            json (dict)       : JSON for the body to attach to the request (if files or data is not specified). e.g. ``{'key1': 'value1', 'key2': 'value2'}``
        """
        headers = self.header.copy()

        if len(json)>0:
            body = js.dumps(json)
            headers["Content-Type"] = "application/json;charset=utf-8"
        elif len(data)>0:
            boundary = f"--------------{uuid.uuid4()}"
            sep_boundary = b"\r\n--" + boundary.encode("ascii")
            end_boundary = sep_boundary + b"--\r\n"
            body = io.BytesIO()
            for key, value in data.items():
                readable = getattr(value, "readable", None)
                if readable and value.readable():
                    filename = "Uploaded file"
                    name_attr = getattr(value, "name", None)
                    if name_attr:
                        filename = name_attr.decode("utf-8") if isinstance(name_attr, bytes) else name_attr
                    if "filename" in data:
                        filename = data["filename"]
                    mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                    title = f'\r\nContent-Disposition: form-data; name="{key}"; filename="{filename}"\r\n"Content-Type: {mimetype}\r\n"'
                    value = value.read()
                else:
                    title = f'\r\nContent-Disposition: form-data; name="{key}"\r\n'
                    value = str(value).encode("utf-8")
                body.write(sep_boundary)
                body.write(title.encode("utf-8"))
                body.write(b"\r\n")
                body.write(value)

            body.write(end_boundary)
            body = body.getvalue()
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
            headers["Content-Length"] = len(body)
        elif len(params)>0:
            body = urllib.parse.urlencode(params)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = None

        if isinstance(body, str):
            body = body.encode("utf-8")

        req = urllib.request.Request(
            url=url,
            data=body,
            method=http_method, 
            headers=headers,
        )
        ret = urllib.request.urlopen(req)
        return ret

    def admin_analytics_getFile(self, type, date="2020-09-01"):
        """Retrieve analytics data for a given date, presented as a compressed JSON file
        
        +--------------+--------------------------+
        | Token type   | Required scope(s)        |
        +==============+==========================+
        | user         | ``admin.analytics:read`` |
        +--------------+--------------------------+

        Args:
            type (str) : The type of analytics to retrieve. The options are currently limited to  ``member`` .(default= ``"member"`` )
            date (str) : Date to retrieve the analytics data for, expressed as  ``YYYY-MM-DD``  in UTC.(default= ``"2020-09-01"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_analytics_getFile(
            ...     type="member",
            ...     date="2020-09-01",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.analytics.getFile", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_apps_approve(self, app_id="A12345", enterprise_id="E12345", request_id="Ar12345", team_id="T1234567890"):
        """Approve an app for installation on a workspace.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.apps:write`` |
        +--------------+----------------------+

        Args:
            app_id (str)        : The id of the app to approve.(default= ``"A12345"`` )
            enterprise_id (str) : The ID of the enterprise to approve the app on(default= ``"E12345"`` )
            request_id (str)    : The id of the request to approve.(default= ``"Ar12345"`` )
            team_id (str)       : The ID of the workspace to approve the app on(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_apps_approve(
            ...     app_id="A12345",
            ...     enterprise_id="E12345",
            ...     request_id="Ar12345",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.apps.approve", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_apps_clearResolution(self, app_id, enterprise_id="E12345", team_id="T1234567890"):
        """Clear an app resolution
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.apps:write`` |
        +--------------+----------------------+

        Args:
            app_id (str)        : The id of the app whose resolution you want to clear/undo.(default= ``"A12345"`` )
            enterprise_id (str) : The enterprise to clear the app resolution from(default= ``"E12345"`` )
            team_id (str)       : The workspace to clear the app resolution from(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_apps_clearResolution(
            ...     app_id="A12345",
            ...     enterprise_id="E12345",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.apps.clearResolution", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_apps_restrict(self, app_id="A12345", enterprise_id="E12345", request_id="Ar12345", team_id="T1234567890"):
        """Restrict an app for installation on a workspace.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.apps:write`` |
        +--------------+----------------------+

        Args:
            app_id (str)        : The id of the app to restrict.(default= ``"A12345"`` )
            enterprise_id (str) : The ID of the enterprise to approve the app on(default= ``"E12345"`` )
            request_id (str)    : The id of the request to restrict.(default= ``"Ar12345"`` )
            team_id (str)       : The ID of the workspace to approve the app on(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_apps_restrict(
            ...     app_id="A12345",
            ...     enterprise_id="E12345",
            ...     request_id="Ar12345",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.apps.restrict", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_apps_approved_list(self, cursor="5c3e53d5", enterprise_id="E0AS553RN", limit=100, team_id="T1234567890"):
        """List approved apps for an org or workspace.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``admin.apps:read`` |
        +--------------+---------------------+

        Args:
            cursor (str)        : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page(default= ``"5c3e53d5"`` )
            enterprise_id (str) : (default= ``"E0AS553RN"`` )
            limit (int)         : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
            team_id (str)       : (default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_apps_approved_list(
            ...     cursor="5c3e53d5",
            ...     enterprise_id="E0AS553RN",
            ...     limit=100,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.apps.approved.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_apps_requests_list(self, cursor="5c3e53d5", limit=100, team_id="T1234567890"):
        """List app requests for a team/workspace.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``admin.apps:read`` |
        +--------------+---------------------+

        Args:
            cursor (str)  : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page(default= ``"5c3e53d5"`` )
            limit (int)   : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
            team_id (str) : (default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_apps_requests_list(
            ...     cursor="5c3e53d5",
            ...     limit=100,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.apps.requests.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_apps_restricted_list(self, cursor="5c3e53d5", enterprise_id="E0AS553RN", limit=100, team_id="T1234567890"):
        """List restricted apps for an org or workspace.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``admin.apps:read`` |
        +--------------+---------------------+

        Args:
            cursor (str)        : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page(default= ``"5c3e53d5"`` )
            enterprise_id (str) : (default= ``"E0AS553RN"`` )
            limit (int)         : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
            team_id (str)       : (default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_apps_restricted_list(
            ...     cursor="5c3e53d5",
            ...     enterprise_id="E0AS553RN",
            ...     limit=100,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.apps.restricted.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_barriers_create(self, barriered_from_usergroup_ids, primary_usergroup_id, restricted_subjects):
        """Create an Information Barrier
        
        +--------------+--------------------------+
        | Token type   | Required scope(s)        |
        +==============+==========================+
        | user         | ``admin.barriers:write`` |
        +--------------+--------------------------+

        Args:
            barriered_from_usergroup_ids (str) : A list of `IDP Groups <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_ ids that the primary usergroup is to be barriered from.
            primary_usergroup_id (str)         : The id of the primary `IDP Group <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_
            restricted_subjects (str)          : What kind of interactions are blocked by this barrier? For v1, we only support a list of all 3, eg  ``im, mpim, call`` 
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_barriers_create(
            ...     barriered_from_usergroup_ids=None,
            ...     primary_usergroup_id=None,
            ...     restricted_subjects=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.barriers.create", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_barriers_delete(self, barrier_id):
        """Delete an existing Information Barrier
        
        +--------------+--------------------------+
        | Token type   | Required scope(s)        |
        +==============+==========================+
        | user         | ``admin.barriers:write`` |
        +--------------+--------------------------+

        Args:
            barrier_id (str) : The ID of the barrier you're trying to delete
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_barriers_delete(
            ...     barrier_id=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.barriers.delete", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_barriers_list(self, cursor="5c3e53d5", limit=100):
        """Get all Information Barriers for your organization
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | user         | ``admin.barriers:read`` |
        +--------------+-------------------------+

        Args:
            cursor (str) : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page(default= ``"5c3e53d5"`` )
            limit (int)  : The maximum number of items to return. Must be between 1 - 1000 both inclusive(default= ``100`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_barriers_list(
            ...     cursor="5c3e53d5",
            ...     limit=100,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.barriers.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_barriers_update(self, barrier_id, barriered_from_usergroup_ids, primary_usergroup_id, restricted_subjects):
        """Update an existing Information Barrier
        
        +--------------+--------------------------+
        | Token type   | Required scope(s)        |
        +==============+==========================+
        | user         | ``admin.barriers:write`` |
        +--------------+--------------------------+

        Args:
            barrier_id (str)                   : The ID of the barrier you're trying to modify
            barriered_from_usergroup_ids (str) : A list of `IDP Groups <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_ ids that the primary usergroup is to be barriered from.
            primary_usergroup_id (str)         : The id of the primary `IDP Group <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_
            restricted_subjects (str)          : What kind of interactions are blocked by this barrier? For v1, we only support a list of all 3, eg  ``im, mpim, call`` 
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_barriers_update(
            ...     barrier_id=None,
            ...     barriered_from_usergroup_ids=None,
            ...     primary_usergroup_id=None,
            ...     restricted_subjects=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.barriers.update", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_conversations_archive(self, channel_id):
        """Archive a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to archive.(default= ``"C12345"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_archive(
            ...     channel_id="C12345",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.archive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_convertToPrivate(self, channel_id):
        """Convert a public channel to a private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to convert to private.(default= ``"C12345"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_convertToPrivate(
            ...     channel_id="C12345",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.convertToPrivate", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_create(self, is_private, name, description="It's a good channel, Bront.", org_wide=True, team_id="T1234567890"):
        """Create a public or private channel-based conversation.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            is_private (bool) : When  ``True`` , creates a private channel instead of a public channel(default= ``True`` )
            name (str)        : Name of the public or private channel to create.(default= ``"mychannel"`` )
            description (str) : Description of the public or private channel to create.(default= ``"It's a good channel, Bront."`` )
            org_wide (bool)   : When  ``True`` , the channel will be available org-wide. Note: if the channel is not  ``org_wide=True`` , you must specify a  ``team_id``  for this channel(default= ``True`` )
            team_id (str)     : The workspace to create the channel in. Note: this argument is required unless you set  ``org_wide=True`` .(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_create(
            ...     is_private=True,
            ...     name="mychannel",
            ...     description="It's a good channel, Bront.",
            ...     org_wide=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.create", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_delete(self, channel_id):
        """Delete a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to delete.(default= ``"C12345"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_delete(
            ...     channel_id="C12345",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.delete", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_disconnectShared(self, channel_id, leaving_team_ids="T123, T4567"):
        """Disconnect a connected channel from one or more workspaces.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
            channel_id (str)       : The channel to be disconnected from some workspaces.(default= ``"C12345"`` )
            leaving_team_ids (str) : The team to be removed from the channel. Currently only a single team id can be specified.(default= ``"T123, T4567"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_disconnectShared(
            ...     channel_id="C12345",
            ...     leaving_team_ids="T123, T4567",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.disconnectShared", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_getConversationPrefs(self, channel_id):
        """Get conversation preferences for a public or private channel.
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            channel_id (str) : The channel to get preferences for.(default= ``"C12345"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_getConversationPrefs(
            ...     channel_id="C12345",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.getConversationPrefs", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_getCustomRetention(self, channel_id):
        """This API endpoint can be used by any admin to get a channel's retention policy.
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            channel_id (str) : The channel to get the retention policy for.(default= ``"C12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_getCustomRetention(
            ...     channel_id="C12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.getCustomRetention", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_getTeams(self, channel_id, cursor="5c3e53d5", limit=100):
        """Get all the workspaces a given public or private channel is connected to within this Enterprise org.
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            channel_id (str) : The channel to determine connected workspaces within the organization for.(default= ``"C12345"`` )
            cursor (str)     : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page(default= ``"5c3e53d5"`` )
            limit (int)      : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_getTeams(
            ...     channel_id="C12345",
            ...     cursor="5c3e53d5",
            ...     limit=100,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.getTeams", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_invite(self, channel_id, user_ids):
        """Invite a user to a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel that the users will be invited to.(default= ``"C12345"`` )
            user_ids (str)   : The users to invite.(default= ``"U1234,U2345,U3456"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_invite(
            ...     channel_id="C12345",
            ...     user_ids="U1234,U2345,U3456",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.invite", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_removeCustomRetention(self, channel_id):
        """This API endpoint can be used by any admin to remove a channel's retention policy.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to set the retention policy for.(default= ``"C12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_removeCustomRetention(
            ...     channel_id="C12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.removeCustomRetention", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_rename(self, channel_id, name):
        """Rename a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to rename.(default= ``"C12345"`` )
            name (str)       : 
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_rename(
            ...     channel_id="C12345",
            ...     name=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.rename", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_search(self, cursor="dXNlcjpVMEc5V0ZYTlo=", limit=20, query="announcement", search_channel_types="private,archived", sort="name", sort_dir="asc", team_ids="T00000000,T00000001"):
        """Search for public or private channels in an Enterprise organization.
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            cursor (str)               : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"dXNlcjpVMEc5V0ZYTlo="`` )
            limit (int)                : Maximum number of items to be returned. Must be between 1 - 20 both inclusive. Default is 10.(default= ``20`` )
            query (str)                : Name of the the channel to query by.(default= ``"announcement"`` )
            search_channel_types (str) : The type of channel to include or exclude in the search. For example  ``private``  will search private channels, while  ``private_exclude``  will exclude them. For a full list of types, check the `Types section <https://api.slack.com/methods/admin.conversations.search#types>`_.(default= ``"private,archived"`` )
            sort (str)                 : Possible values are  ``relevant``  (search ranking based on what we think is closest),  ``name``  (alphabetical),  ``member_count``  (number of users in the channel), and  ``created``  (date channel was created). You can optionally pair this with the  ``sort_dir``  arg to change how it is sorted(default= ``"name"`` )
            sort_dir (str)             : Sort direction. Possible values are  ``asc``  for ascending order like (1, 2, 3) or (a, b, c), and  ``desc``  for descending order like (3, 2, 1) or (c, b, a)(default= ``"asc"`` )
            team_ids (str)             : Comma separated string of team IDs, signifying the workspaces to search through.(default= ``"T00000000,T00000001"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_search(
            ...     cursor="dXNlcjpVMEc5V0ZYTlo=",
            ...     limit=20,
            ...     query="announcement",
            ...     search_channel_types="private,archived",
            ...     sort="name",
            ...     sort_dir="asc",
            ...     team_ids="T00000000,T00000001",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.search", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_setConversationPrefs(self, channel_id, prefs):
        """Set the posting permissions for a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to set the prefs for(default= ``"C1234"`` )
            prefs (dict)     : The prefs for this channel in a stringified JSON format.(default= ``{'who_can_post': 'type:admin,user:U1234,subteam:S1234'}`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_setConversationPrefs(
            ...     channel_id="C1234",
            ...     prefs={'who_can_post': 'type:admin,user:U1234,subteam:S1234'},
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.setConversationPrefs", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_setCustomRetention(self, channel_id, duration_days):
        """This API endpoint can be used by any admin to set a channel's retention policy.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str)    : The channel to set the retention policy for.(default= ``"C12345678"`` )
            duration_days (int) : The message retention duration in days to set for this channel(default= ``500`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_setCustomRetention(
            ...     channel_id="C12345678",
            ...     duration_days=500,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.setCustomRetention", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_setTeams(self, channel_id, org_channel=True, target_team_ids="T1234,T5678,T9012,T3456", team_id="T1234567890"):
        """Set the workspaces in an Enterprise grid org that connect to a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str)      : The encoded  ``channel_id``  to add or remove to workspaces.
            org_channel (bool)    : True if channel has to be converted to an org channel(default= ``True`` )
            target_team_ids (str) : A comma-separated list of workspaces to which the channel should be shared. Not required if the channel is being shared org-wide.(default= ``"T1234,T5678,T9012,T3456"`` )
            team_id (str)         : The workspace to which the channel belongs. Omit this argument if the channel is a cross-workspace shared channel.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_setTeams(
            ...     channel_id=None,
            ...     org_channel=True,
            ...     target_team_ids="T1234,T5678,T9012,T3456",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.setTeams", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_unarchive(self, channel_id):
        """Unarchive a public or private channel.
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to unarchive.(default= ``"C12345"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_unarchive(
            ...     channel_id="C12345",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.unarchive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_ekm_listOriginalConnectedChannelInfo(self, channel_ids=None, cursor="5c3e53d5", limit=100, team_ids=None):
        """List all disconnected channelsâ€”i.e., channels that were once connected to other workspaces and then disconnectedâ€”and the corresponding original channel IDs for key revocation with EKM.
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            channel_ids (str) : A comma-separated list of channels to filter to.
            cursor (str)      : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"5c3e53d5"`` )
            limit (int)       : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
            team_ids (str)    : A comma-separated list of the workspaces to which the channels you would like returned belong.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_ekm_listOriginalConnectedChannelInfo(
            ...     channel_ids=None,
            ...     cursor="5c3e53d5",
            ...     limit=100,
            ...     team_ids=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.ekm.listOriginalConnectedChannelInfo", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_conversations_restrictAccess_addGroup(self, channel_id, group_id, team_id="T1234567890"):
        """Add an allowlist of IDP groups for accessing a channel
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to link this group to.
            group_id (str)   : The `IDP Group <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_ ID to be an allowlist for the private channel.
            team_id (str)    : The workspace where the channel exists. This argument is required for channels only tied to one workspace, and optional for channels that are shared across an organization.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_restrictAccess_addGroup(
            ...     channel_id=None,
            ...     group_id=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.restrictAccess.addGroup", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_conversations_restrictAccess_listGroups(self, channel_id, team_id="T1234567890"):
        """List all IDP Groups linked to a channel
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            channel_id (str) : 
            team_id (str)    : The workspace where the channel exists. This argument is required for channels only tied to one workspace, and optional for channels that are shared across an organization.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_restrictAccess_listGroups(
            ...     channel_id=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.restrictAccess.listGroups", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_conversations_restrictAccess_removeGroup(self, channel_id, group_id, team_id):
        """Remove a linked IDP group linked from a private channel
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to remove the linked group from.
            group_id (str)   : The `IDP Group <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_ ID to remove from the private channel.
            team_id (str)    : The workspace where the channel exists. This argument is required for channels only tied to one workspace, and optional for channels that are shared across an organization.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_restrictAccess_removeGroup(
            ...     channel_id=None,
            ...     group_id=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.restrictAccess.removeGroup", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_emoji_add(self, name, url):
        """Add an emoji.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            name (str) : The name of the emoji to be added. Colons ( ``:myemoji:`` ) around the value are not required, although they may be included.
            url (str)  : The URL of a file to use as an image for the emoji. Square images under 128KB and with transparent backgrounds work best.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_emoji_add(
            ...     name=None,
            ...     url=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.emoji.add", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_emoji_addAlias(self, alias_for, name):
        """Add an emoji alias.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            alias_for (str) : The alias of the emoji.
            name (str)      : The name of the emoji to be aliased. Colons ( ``:myemoji:`` ) around the value are not required, although they may be included.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_emoji_addAlias(
            ...     alias_for=None,
            ...     name=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.emoji.addAlias", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_emoji_list(self, cursor="5c3e53d5", limit=100):
        """List emoji for an Enterprise Grid organization.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.teams:read`` |
        +--------------+----------------------+

        Args:
            cursor (str) : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page(default= ``"5c3e53d5"`` )
            limit (int)  : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_emoji_list(
            ...     cursor="5c3e53d5",
            ...     limit=100,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.emoji.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_emoji_remove(self, name):
        """Remove an emoji across an Enterprise Grid organization
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            name (str) : The name of the emoji to be removed. Colons ( ``:myemoji:`` ) around the value are not required, although they may be included.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_emoji_remove(
            ...     name=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.emoji.remove", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_emoji_rename(self, name, new_name):
        """Rename an emoji.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            name (str)     : The name of the emoji to be renamed. Colons ( ``:myemoji:`` ) around the value are not required, although they may be included.
            new_name (str) : The new name of the emoji.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_emoji_rename(
            ...     name=None,
            ...     new_name=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.emoji.rename", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_inviteRequests_approve(self, invite_request_id, team_id="T1234567890"):
        """Approve a workspace invite request.
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | user         | ``admin.invites:write`` |
        +--------------+-------------------------+

        Args:
            invite_request_id (str) : ID of the request to invite.(default= ``"Ir1234"`` )
            team_id (str)           : ID for the workspace where the invite request was made.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_inviteRequests_approve(
            ...     invite_request_id="Ir1234",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.inviteRequests.approve", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_inviteRequests_deny(self, invite_request_id, team_id="T1234567890"):
        """Deny a workspace invite request.
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | user         | ``admin.invites:write`` |
        +--------------+-------------------------+

        Args:
            invite_request_id (str) : ID of the request to invite.(default= ``"Ir1234"`` )
            team_id (str)           : ID for the workspace where the invite request was made.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_inviteRequests_deny(
            ...     invite_request_id="Ir1234",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.inviteRequests.deny", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_inviteRequests_list(self, cursor="5cweb43", limit=100, team_id="T1234567890"):
        """List all pending workspace invite requests.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | user         | ``admin.invites:read`` |
        +--------------+------------------------+

        Args:
            cursor (str)  : Value of the  ``next_cursor``  field sent as part of the previous API response(default= ``"5cweb43"`` )
            limit (int)   : The number of results that will be returned by the API on each invocation. Must be between 1 - 1000, both inclusive(default= ``100`` )
            team_id (str) : ID for the workspace where the invite requests were made.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_inviteRequests_list(
            ...     cursor="5cweb43",
            ...     limit=100,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.inviteRequests.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_inviteRequests_approved_list(self, cursor="5cweb43", limit=100, team_id="T1234567890"):
        """List all approved workspace invite requests.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | user         | ``admin.invites:read`` |
        +--------------+------------------------+

        Args:
            cursor (str)  : Value of the  ``next_cursor``  field sent as part of the previous API response(default= ``"5cweb43"`` )
            limit (int)   : The number of results that will be returned by the API on each invocation. Must be between 1 - 1000, both inclusive(default= ``100`` )
            team_id (str) : ID for the workspace where the invite requests were made.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_inviteRequests_approved_list(
            ...     cursor="5cweb43",
            ...     limit=100,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.inviteRequests.approved.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_inviteRequests_denied_list(self, cursor="5cweb43", limit=100, team_id="T1234567890"):
        """List all denied workspace invite requests.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | user         | ``admin.invites:read`` |
        +--------------+------------------------+

        Args:
            cursor (str)  : Value of the  ``next_cursor``  field sent as part of the previous api response(default= ``"5cweb43"`` )
            limit (int)   : The number of results that will be returned by the API on each invocation. Must be between 1 - 1000 both inclusive(default= ``100`` )
            team_id (str) : ID for the workspace where the invite requests were made.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_inviteRequests_denied_list(
            ...     cursor="5cweb43",
            ...     limit=100,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.inviteRequests.denied.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_teams_admins_list(self, team_id, cursor="dXNlcjpVMEc5V0ZYTlo=", limit=200):
        """List all of the admins on a given workspace.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.teams:read`` |
        +--------------+----------------------+

        Args:
            team_id (str) : (default= ``"T1234567890"`` )
            cursor (str)  : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"dXNlcjpVMEc5V0ZYTlo="`` )
            limit (int)   : The maximum number of items to return.(default= ``200`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_admins_list(
            ...     team_id="T1234567890",
            ...     cursor="dXNlcjpVMEc5V0ZYTlo=",
            ...     limit=200,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.admins.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_teams_create(self, team_domain, team_name, team_description=None, team_discoverability=None):
        """Create an Enterprise team.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            team_domain (str)          : Team domain (for example, slacksoftballteam).
            team_name (str)            : Team name (for example, Slack Softball Team).
            team_description (str)     : Description for the team.
            team_discoverability (str) : Who can join the team. A team's discoverability can be  ``open`` ,  ``closed`` ,  ``invite_only`` , or  ``unlisted`` .
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_create(
            ...     team_domain=None,
            ...     team_name=None,
            ...     team_description=None,
            ...     team_discoverability=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.create", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_teams_list(self, cursor="5c3e53d5", limit=50):
        """List all teams on an Enterprise organization
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.teams:read`` |
        +--------------+----------------------+

        Args:
            cursor (str) : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"5c3e53d5"`` )
            limit (int)  : The maximum number of items to return. Must be between 1 - 100 both inclusive.(default= ``50`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_list(
            ...     cursor="5c3e53d5",
            ...     limit=50,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_teams_owners_list(self, team_id, cursor="5c3e53d5", limit=100):
        """List all of the owners on a given workspace.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.teams:read`` |
        +--------------+----------------------+

        Args:
            team_id (str) : (default= ``"T1234567890"`` )
            cursor (str)  : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"5c3e53d5"`` )
            limit (int)   : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_owners_list(
            ...     team_id="T1234567890",
            ...     cursor="5c3e53d5",
            ...     limit=100,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.owners.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_teams_settings_info(self, team_id):
        """Fetch information about settings in a workspace
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.teams:read`` |
        +--------------+----------------------+

        Args:
            team_id (str) : (default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_settings_info(
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.settings.info", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_teams_settings_setDefaultChannels(self, channel_ids, team_id):
        """Set the default channels of a workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            channel_ids (str) : An array of channel IDs.
            team_id (str)     : ID for the workspace to set the default channel for.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_settings_setDefaultChannels(
            ...     channel_ids=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.settings.setDefaultChannels", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_teams_settings_setDescription(self, description, team_id):
        """Set the description of a given workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            description (str) : The new description for the workspace.
            team_id (str)     : ID for the workspace to set the description for.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_settings_setDescription(
            ...     description=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.settings.setDescription", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_teams_settings_setDiscoverability(self, discoverability, team_id):
        """An API method that allows admins to set the discoverability of a given workspace
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            discoverability (str) : This workspace's discovery setting. It must be set to one of  ``open`` ,  ``invite_only`` ,  ``closed`` , or  ``unlisted`` .
            team_id (str)         : The ID of the workspace to set discoverability on.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_settings_setDiscoverability(
            ...     discoverability=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.settings.setDiscoverability", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_teams_settings_setIcon(self, image_url, team_id):
        """Sets the icon of a workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            image_url (str) : Image URL for the icon(default= ``"http://mysite.com/icon.jpeg"`` )
            team_id (str)   : ID for the workspace to set the icon for.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_settings_setIcon(
            ...     image_url="http://mysite.com/icon.jpeg",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.settings.setIcon", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_teams_settings_setName(self, name, team_id):
        """Set the name of a given workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            name (str)    : The new name of the workspace.
            team_id (str) : ID for the workspace to set the name for.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_teams_settings_setName(
            ...     name=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.teams.settings.setName", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_usergroups_addChannels(self, channel_ids, usergroup_id, team_id="T1234567890"):
        """Add up to one hundred default channels to an IDP group.
        
        +--------------+----------------------------+
        | Token type   | Required scope(s)          |
        +==============+============================+
        | user         | ``admin.usergroups:write`` |
        +--------------+----------------------------+

        Args:
            channel_ids (str)  : Comma separated string of channel IDs.(default= ``"C00000000,C00000001"`` )
            usergroup_id (str) : ID of the IDP group to add default channels for.(default= ``"S00000000"`` )
            team_id (str)      : The workspace to add default channels in.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_usergroups_addChannels(
            ...     channel_ids="C00000000,C00000001",
            ...     usergroup_id="S00000000",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.usergroups.addChannels", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_usergroups_addTeams(self, team_ids, usergroup_id, auto_provision=True):
        """Associate one or more default workspaces with an organization-wide IDP group.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.teams:write`` |
        +--------------+-----------------------+

        Args:
            team_ids (str)        : A comma separated list of encoded team (workspace) IDs. Each workspace <em>MUST</em> belong to the organization associated with the token.(default= ``"T12345678,T98765432"`` )
            usergroup_id (str)    : An encoded usergroup (IDP Group) ID.(default= ``"S12345678"`` )
            auto_provision (bool) : When  ``True`` , this method automatically creates new workspace accounts for the IDP group members.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_usergroups_addTeams(
            ...     team_ids="T12345678,T98765432",
            ...     usergroup_id="S12345678",
            ...     auto_provision=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.usergroups.addTeams", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_usergroups_listChannels(self, usergroup_id, include_num_members=True, team_id="T1234567890"):
        """List the channels linked to an org-level IDP group (user group).
        
        +--------------+---------------------------+
        | Token type   | Required scope(s)         |
        +==============+===========================+
        | user         | ``admin.usergroups:read`` |
        +--------------+---------------------------+

        Args:
            usergroup_id (str)         : ID of the IDP group to list default channels for.(default= ``"S00000000"`` )
            include_num_members (bool) : Flag to include or exclude the count of members per channel.(default= ``True`` )
            team_id (str)              : ID of the the workspace.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_usergroups_listChannels(
            ...     usergroup_id="S00000000",
            ...     include_num_members=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.usergroups.listChannels", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_usergroups_removeChannels(self, channel_ids, usergroup_id):
        """Remove one or more default channels from an org-level IDP group (user group).
        
        +--------------+----------------------------+
        | Token type   | Required scope(s)          |
        +==============+============================+
        | user         | ``admin.usergroups:write`` |
        +--------------+----------------------------+

        Args:
            channel_ids (str)  : Comma-separated string of channel IDs(default= ``"C00000000,C00000001"`` )
            usergroup_id (str) : ID of the IDP Group(default= ``"S00000000"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_usergroups_removeChannels(
            ...     channel_ids="C00000000,C00000001",
            ...     usergroup_id="S00000000",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.usergroups.removeChannels", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_assign(self, team_id, user_id, channel_ids="C123,C3456", is_restricted=True, is_ultra_restricted=True):
        """Add an Enterprise user to a workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            team_id (str)              : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
            user_id (str)              : The ID of the user to add to the workspace.
            channel_ids (str)          : Comma separated values of channel IDs to add user in the new workspace.(default= ``"C123,C3456"`` )
            is_restricted (bool)       : True if user should be added to the workspace as a guest.(default= ``True`` )
            is_ultra_restricted (bool) : True if user should be added to the workspace as a single-channel guest.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_assign(
            ...     team_id="T1234567890",
            ...     user_id=None,
            ...     channel_ids="C123,C3456",
            ...     is_restricted=True,
            ...     is_ultra_restricted=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.assign", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_invite(self, channel_ids, email, team_id, custom_message="Come and join our team!", guest_expiration_ts=123456789.012345, is_restricted=True, is_ultra_restricted=True, real_name={'full_name': 'Joe Smith'}, resend=True):
        """Invite a user to a workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            channel_ids (str)           : A comma-separated list of  ``channel_id`` s for this user to join. At least one channel is required.(default= ``"C1A2B3C4D,C26Z25Y24"`` )
            email (str)                 : The email address of the person to invite.(default= ``"joe@email.com"`` )
            team_id (str)               : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
            custom_message (str)        : An optional message to send to the user in the invite email.(default= ``"Come and join our team!"`` )
            guest_expiration_ts (float) : Timestamp when guest account should be disabled. Only include this timestamp if you are inviting a guest user and you want their account to expire on a certain date.(default= ``123456789.012345`` )
            is_restricted (bool)        : Is this user a multi-channel guest user? (default: False)(default= ``True`` )
            is_ultra_restricted (bool)  : Is this user a single channel guest user? (default: False)(default= ``True`` )
            real_name (dict)            : Full name of the user.(default= ``{'full_name': 'Joe Smith'}`` )
            resend (bool)               : Allow this invite to be resent in the future if a user has not signed up yet. (default: False)(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_invite(
            ...     channel_ids="C1A2B3C4D,C26Z25Y24",
            ...     email="joe@email.com",
            ...     team_id="T1234567890",
            ...     custom_message="Come and join our team!",
            ...     guest_expiration_ts=123456789.012345,
            ...     is_restricted=True,
            ...     is_ultra_restricted=True,
            ...     real_name={'full_name': 'Joe Smith'},
            ...     resend=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.invite", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_list(self, cursor="5c3e53d5", limit=50, team_id="T1234567890"):
        """List users on a workspace
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.users:read`` |
        +--------------+----------------------+

        Args:
            cursor (str)  : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"5c3e53d5"`` )
            limit (int)   : Limit for how many users to be retrieved per page(default= ``50`` )
            team_id (str) : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_list(
            ...     cursor="5c3e53d5",
            ...     limit=50,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_remove(self, team_id, user_id):
        """Remove a user from a workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            team_id (str) : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
            user_id (str) : The ID of the user to remove.(default= ``"W12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_remove(
            ...     team_id="T1234567890",
            ...     user_id="W12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.remove", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_setAdmin(self, team_id, user_id):
        """Set an existing guest, regular user, or owner to be an admin user.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            team_id (str) : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
            user_id (str) : The ID of the user to designate as an admin.(default= ``"W12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_setAdmin(
            ...     team_id="T1234567890",
            ...     user_id="W12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.setAdmin", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_setExpiration(self, expiration_ts, user_id, team_id="T1234567890"):
        """Set an expiration for a guest user
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            expiration_ts (int) : Timestamp when guest account should be disabled.(default= ``1234567890`` )
            user_id (str)       : The ID of the user to set an expiration for.(default= ``"W12345678"`` )
            team_id (str)       : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_setExpiration(
            ...     expiration_ts=1234567890,
            ...     user_id="W12345678",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.setExpiration", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_setOwner(self, team_id, user_id):
        """Set an existing guest, regular user, or admin user to be a workspace owner.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            team_id (str) : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
            user_id (str) : Id of the user to promote to owner.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_setOwner(
            ...     team_id="T1234567890",
            ...     user_id=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.setOwner", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_setRegular(self, team_id, user_id):
        """Set an existing guest user, admin user, or owner to be a regular user.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            team_id (str) : The ID ( ``T1234`` ) of the workspace.(default= ``"T1234567890"`` )
            user_id (str) : The ID of the user to designate as a regular user.(default= ``"W12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_setRegular(
            ...     team_id="T1234567890",
            ...     user_id="W12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.setRegular", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_session_invalidate(self, session_id, team_id):
        """Revoke a single session for a user. The user will be forced to login to Slack.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            session_id (int) : ID of the session to invalidate.(default= ``12345`` )
            team_id (str)    : ID of the workspace that the session belongs to.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_session_invalidate(
            ...     session_id=12345,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.session.invalidate", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_session_list(self, cursor="5c3e53d5", limit=100, team_id="T1234567890", user_id="U1234"):
        """List active user sessions for an organization
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | user         | ``admin.users:read`` |
        +--------------+----------------------+

        Args:
            cursor (str)  : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"5c3e53d5"`` )
            limit (int)   : The maximum number of items to return. Must be between 1 - 1000 both inclusive.(default= ``100`` )
            team_id (str) : The ID of the workspace you'd like active sessions for. If you pass a  ``team_id`` , you'll need to pass a  ``user_id``  as well.(default= ``"T1234567890"`` )
            user_id (str) : The ID of user you'd like active sessions for. If you pass a  ``user_id`` , you'll need to pass a  ``team_id``  as well.(default= ``"U1234"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_session_list(
            ...     cursor="5c3e53d5",
            ...     limit=100,
            ...     team_id="T1234567890",
            ...     user_id="U1234",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.session.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_users_session_reset(self, user_id, mobile_only=True, web_only=True):
        """Wipes all valid sessions on all devices for a given user
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``admin.users:write`` |
        +--------------+-----------------------+

        Args:
            user_id (str)      : The ID of the user to wipe sessions for(default= ``"W12345678"`` )
            mobile_only (bool) : Only expire mobile sessions (default: False)(default= ``True`` )
            web_only (bool)    : Only expire web sessions (default: False)(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_users_session_reset(
            ...     user_id="W12345678",
            ...     mobile_only=True,
            ...     web_only=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.users.session.reset", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def api_test(self):
        """Checks API calling code.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.api_test(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="api.test", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def apps_event_authorizations_list(self, event_context, cursor=None, limit=None):
        """Get a list of authorizations for the given event context. Each authorization represents an app installation that the event is visible to.
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | app-level    | ``authorizations:read`` |
        +--------------+-------------------------+

        Args:
            event_context (str) : 
            cursor (str)        : 
            limit (str)         : 
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_event_authorizations_list(
            ...     event_context=None,
            ...     cursor=None,
            ...     limit=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.event.authorizations.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def apps_permissions_info(self):
        """Returns list of permissions this app has on a team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_permissions_info(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.permissions.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def apps_permissions_request(self, scopes, trigger_id):
        """Allows an app to request additional scopes
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
            scopes (str)     : A comma separated list of scopes to request for
            trigger_id (str) : Token used to trigger the permissions API
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_permissions_request(
            ...     scopes=None,
            ...     trigger_id=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.permissions.request", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def apps_permissions_resources_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20):
        """Returns list of resource grants this app has on a team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
            cursor (str) : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)  : The maximum number of items to return.(default= ``20`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_permissions_resources_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.permissions.resources.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def apps_permissions_scopes_list(self):
        """Returns list of scopes this app has on a team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_permissions_scopes_list(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.permissions.scopes.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def apps_permissions_users_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20):
        """Returns list of user grants and corresponding scopes this app has on a team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
            cursor (str) : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)  : The maximum number of items to return.(default= ``20`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_permissions_users_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.permissions.users.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def apps_permissions_users_request(self, scopes, trigger_id, user):
        """Enables an app to trigger a permissions modal to grant an app access to a user access scope.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        +--------------+---------------------+

        Args:
            scopes (str)     : A comma separated list of user scopes to request for
            trigger_id (str) : Token used to trigger the request
            user (str)       : The user this scope is being requested for
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_permissions_users_request(
            ...     scopes=None,
            ...     trigger_id=None,
            ...     user=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.permissions.users.request", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def apps_uninstall(self, client_id, client_secret):
        """Uninstalls your app from a workspace.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+

        Args:
            client_id (float)   : Issued when you created your application.(default= ``56579136444.26251`` )
            client_secret (str) : Issued when you created your application.(default= ``"f25b5ceaf8a3c2a2c4f52bb4f0b0499e"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.apps_uninstall(
            ...     client_id=56579136444.26251,
            ...     client_secret="f25b5ceaf8a3c2a2c4f52bb4f0b0499e",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="apps.uninstall", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def auth_revoke(self, test=True):
        """Revokes a token.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            test (bool) : Setting this parameter to  ``1``  triggers a <em>testing mode</em> where the specified token will not actually be revoked.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.auth_revoke(
            ...     test=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="auth.revoke", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def auth_test(self):
        """Checks authentication & identity.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+
        | app-level    | ``No scope required`` |
        +--------------+-----------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.auth_test(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="auth.test", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def auth_teams_list(self, cursor="5c3e53d5", include_icon=False, limit=50):
        """List the workspaces a token can access.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+

        Args:
            cursor (str)        : Set  ``cursor``  to  ``next_cursor``  returned by the previous call to list items in the next page.(default= ``"5c3e53d5"`` )
            include_icon (bool) : Whether to return icon paths for each workspace. An icon path represents a URI pointing to the image signifying the workspace.
            limit (int)         : The maximum number of workspaces to return. Must be a positive integer no larger than 1000.(default= ``50`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.auth_teams_list(
            ...     cursor="5c3e53d5",
            ...     include_icon=False,
            ...     limit=50,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="auth.teams.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def bots_info(self, bot="B12345678", team_id="T1234567890"):
        """Gets information about a bot user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``users:read``      |
        +--------------+---------------------+
        | user         | ``users:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            bot (str)     : Bot user to get info on(default= ``"B12345678"`` )
            team_id (str) : encoded team id or enterprise id where the bot exists, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.bots_info(
            ...     bot="B12345678",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="bots.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def calls_add(self, external_unique_id, join_url, created_by="U1H77", date_start=1562002086, desktop_app_join_url="callapp://join/1234567890", external_display_id="705-292-868", title="Kimpossible sync up", users=[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}]):
        """Registers a new Call.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``calls:write``     |
        +--------------+---------------------+
        | user         | ``calls:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            external_unique_id (str)   : An ID supplied by the 3rd-party Call provider. It must be unique across all Calls from that service.(default= ``"025169F6-E37A-4E62-BB54-7F93A0FC4C1F"`` )
            join_url (str)             : The URL required for a client to join the Call.(default= ``"https://example.com/calls/1234567890"`` )
            created_by (str)           : The valid Slack user ID of the user who created this Call. When this method is called with a user token, the  ``created_by``  field is optional and defaults to the authed user of the token. Otherwise, the field is required.(default= ``"U1H77"`` )
            date_start (int)           : Call start time in UTC UNIX timestamp format(default= ``1562002086`` )
            desktop_app_join_url (str) : When supplied, available Slack clients will attempt to directly launch the 3rd-party Call with this URL.(default= ``"callapp://join/1234567890"`` )
            external_display_id (int)  : An optional, human-readable ID supplied by the 3rd-party Call provider. If supplied, this ID will be displayed in the Call object.(default= ``"705-292-868"`` )
            title (str)                : The name of the Call.(default= ``"Kimpossible sync up"`` )
            users (list)               : The list of users to register as participants in the Call. `Read more on how to specify users here <https://api.slack.com/apis/calls#users>`_.(default= ``[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}]`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.calls_add(
            ...     external_unique_id="025169F6-E37A-4E62-BB54-7F93A0FC4C1F",
            ...     join_url="https://example.com/calls/1234567890",
            ...     created_by="U1H77",
            ...     date_start=1562002086,
            ...     desktop_app_join_url="callapp://join/1234567890",
            ...     external_display_id="705-292-868",
            ...     title="Kimpossible sync up",
            ...     users=[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}],
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="calls.add", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def calls_end(self, id, duration=1800):
        """Ends a Call.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``calls:write``     |
        +--------------+---------------------+
        | user         | ``calls:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            id (str)       :  ``id``  returned when registering the call using the  ``calls.add``  method.(default= ``"R0E69JAIF"`` )
            duration (int) : Call duration in seconds(default= ``1800`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.calls_end(
            ...     id="R0E69JAIF",
            ...     duration=1800,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="calls.end", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def calls_info(self, id):
        """Returns information about a Call.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``calls:read``      |
        +--------------+---------------------+
        | user         | ``calls:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            id (str) :  ``id``  of the Call returned by the  ``calls.add``  method.(default= ``"R0E69JAIF"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.calls_info(
            ...     id="R0E69JAIF",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="calls.info", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def calls_update(self, id, desktop_app_join_url="callapp://join/0987654321", join_url="https://example.com/calls/0987654321", title="Kimpossible sync up call"):
        """Updates information about a Call.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``calls:write``     |
        +--------------+---------------------+
        | user         | ``calls:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            id (str)                   :  ``id``  returned by the  ``calls.add``  method.(default= ``"R0E69JAIF"`` )
            desktop_app_join_url (str) : When supplied, available Slack clients will attempt to directly launch the 3rd-party Call with this URL.(default= ``"callapp://join/0987654321"`` )
            join_url (str)             : The URL required for a client to join the Call.(default= ``"https://example.com/calls/0987654321"`` )
            title (str)                : The name of the Call.(default= ``"Kimpossible sync up call"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.calls_update(
            ...     id="R0E69JAIF",
            ...     desktop_app_join_url="callapp://join/0987654321",
            ...     join_url="https://example.com/calls/0987654321",
            ...     title="Kimpossible sync up call",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="calls.update", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def calls_participants_add(self, id, users):
        """Registers new participants added to a Call.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``calls:write``     |
        +--------------+---------------------+
        | user         | ``calls:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            id (str)     :  ``id``  returned by the  ``calls.add``  method.(default= ``"R0E69JAIF"`` )
            users (list) : The list of users to add as participants in the Call. `Read more on how to specify users here <https://api.slack.com/apis/calls#users>`_.(default= ``[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}]`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.calls_participants_add(
            ...     id="R0E69JAIF",
            ...     users=[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}],
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="calls.participants.add", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def calls_participants_remove(self, id, users):
        """Registers participants removed from a Call.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``calls:write``     |
        +--------------+---------------------+
        | user         | ``calls:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            id (str)     :  ``id``  returned by the  ``calls.add``  method.(default= ``"R0E69JAIF"`` )
            users (list) : The list of users to remove as participants in the Call. `Read more on how to specify users here <https://api.slack.com/apis/calls#users>`_.(default= ``[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}]`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.calls_participants_remove(
            ...     id="R0E69JAIF",
            ...     users=[{'slack_id': 'U1H77'}, {'external_id': '54321678', 'display_name': 'External User', 'avatar_url': 'https://example.com/users/avatar1234.jpg'}],
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="calls.participants.remove", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_delete(self, channel, ts, as_user=True):
        """Deletes a message.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:user``, ``chat:write:bot`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            channel (str)  : Channel containing the message to be deleted.(default= ``"C1234567890"`` )
            ts (float)     : Timestamp of the message to be deleted.(default= ``1405894322.002768`` )
            as_user (bool) : Pass True to delete the message as the authed user with  ``chat:write:user``  scope. `Bot users <https://api.slack.com/bot-users>`_ in this context are considered authed users. If unused or False, the message will be deleted with  ``chat:write:bot``  scope.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_delete(
            ...     channel="C1234567890",
            ...     ts=1405894322.002768,
            ...     as_user=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.delete", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_deleteScheduledMessage(self, channel, scheduled_message_id, as_user=True):
        """Deletes a pending scheduled message from the queue.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:user``, ``chat:write:bot`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            channel (str)              : The channel the scheduled_message is posting to(default= ``"C123456789"`` )
            scheduled_message_id (str) :  ``scheduled_message_id``  returned from call to chat.scheduleMessage(default= ``"Q1234ABCD"`` )
            as_user (bool)             : Pass True to delete the message as the authed user with  ``chat:write:user``  scope. `Bot users <https://api.slack.com/bot-users>`_ in this context are considered authed users. If unused or False, the message will be deleted with  ``chat:write:bot``  scope.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_deleteScheduledMessage(
            ...     channel="C123456789",
            ...     scheduled_message_id="Q1234ABCD",
            ...     as_user=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.deleteScheduledMessage", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_getPermalink(self, channel, message_ts):
        """Retrieve a permalink URL for a specific extant message
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            channel (int)      : The ID of the conversation or channel containing the message(default= ``53072`` )
            message_ts (float) : A message's  ``ts``  value, uniquely identifying it within a channel(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_getPermalink(
            ...     channel=53072,
            ...     message_ts=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.getPermalink", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def chat_meMessage(self, channel, text):
        """Share a me message into a channel.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:bot``, ``chat:write:user`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            channel (str) : Channel to send message to. Can be a public channel, private group or IM channel. Can be an encoded ID, or a name.(default= ``"C1234567890"`` )
            text (str)    : Text of the message to send.(default= ``"Hello world"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_meMessage(
            ...     channel="C1234567890",
            ...     text="Hello world",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.meMessage", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_postEphemeral(self, attachments, channel, text, user, as_user=True, blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}], icon_emoji=":chart_with_upwards_trend:", icon_url="http://lorempixel.com/48/48", link_names=True, parse="full", thread_ts=1234567890.123456, username="My Bot"):
        """Sends an ephemeral message to a user in a channel.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:user``, ``chat:write:bot`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            attachments (list) : A JSON-based array of structured attachments, presented as a URL-encoded string.(default= ``[{'pretext': 'pre-hello', 'text': 'text-world'}]`` )
            channel (str)      : Channel, private group, or IM channel to send message to. Can be an encoded ID, or a name.(default= ``"C1234567890"`` )
            text (str)         : How this field works and whether it is required depends on other fields you use in your API call. `See here <https://api.slack.com/methods/chat.postEphemeral#text_usage>`_ for more detail.(default= ``"Hello world"`` )
            user (str)         :  ``id``  of the user who will receive the ephemeral message. The user should be in the channel specified by the  ``channel``  argument.(default= ``"U0BPQUNTA"`` )
            as_user (bool)     : Pass True to post the message as the authed user. Defaults to True if the chat:write:bot scope is not included. Otherwise, defaults to False.(default= ``True`` )
            blocks (list)      : A JSON-based array of structured blocks, presented as a URL-encoded string.(default= ``[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}]`` )
            icon_emoji (str)   : Emoji to use as the icon for this message. Overrides  ``icon_url`` . Must be used in conjunction with  ``as_user``  set to  ``False`` , otherwise ignored. See `authorship <https://api.slack.com/methods/chat.postEphemeral#authorship>`_ here.(default= ``":chart_with_upwards_trend:"`` )
            icon_url (str)     : URL to an image to use as the icon for this message. Must be used in conjunction with  ``as_user``  set to False, otherwise ignored. See `authorship <https://api.slack.com/methods/chat.postEphemeral#authorship>`_ here.(default= ``"http://lorempixel.com/48/48"`` )
            link_names (bool)  : Find and link channel names and usernames.(default= ``True`` )
            parse (str)        : Change how messages are treated. Defaults to  ``None`` . See `here <https://api.slack.com/methods/chat.postEphemeral#formatting>`_.(default= ``"full"`` )
            thread_ts (float)  : Provide another message's  ``ts``  value to post this message in a thread. Avoid using a reply's  ``ts``  value; use its parent's value instead. Ephemeral messages in threads are only shown if there is already an active thread.(default= ``1234567890.123456`` )
            username (str)     : Set your bot's user name. Must be used in conjunction with  ``as_user``  set to False, otherwise ignored. See `authorship <https://api.slack.com/methods/chat.postEphemeral#authorship>`_ here.(default= ``"My Bot"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_postEphemeral(
            ...     attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}],
            ...     channel="C1234567890",
            ...     text="Hello world",
            ...     user="U0BPQUNTA",
            ...     as_user=True,
            ...     blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}],
            ...     icon_emoji=":chart_with_upwards_trend:",
            ...     icon_url="http://lorempixel.com/48/48",
            ...     link_names=True,
            ...     parse="full",
            ...     thread_ts=1234567890.123456,
            ...     username="My Bot",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.postEphemeral", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_postMessage(self, channel, text, as_user=True, attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}], blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}], icon_emoji=":chart_with_upwards_trend:", icon_url="http://lorempixel.com/48/48", link_names=True, mrkdwn=False, parse="full", reply_broadcast=True, thread_ts=1234567890.123456, unfurl_links=True, unfurl_media=False, username="My Bot"):
        """Sends a message to a channel.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:user``, ``chat:write:bot`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            channel (str)          : Channel, private group, or IM channel to send message to. Can be an encoded ID, or a name. See `here <https://api.slack.com/methods/chat.postMessage#channels>`_ for more details.(default= ``"C1234567890"`` )
            text (str)             : How this field works and whether it is required depends on other fields you use in your API call. `See here <https://api.slack.com/methods/chat.postMessage#text_usage>`_ for more detail.(default= ``"Hello world"`` )
            as_user (bool)         : Pass True to post the message as the authed user, instead of as a bot. Defaults to False. See `authorship <https://api.slack.com/methods/chat.postMessage#authorship>`_ here. This argument may not be used with newer `bot tokens <https://api.slack.com/docs/token-types#granular_bot>`_.(default= ``True`` )
            attachments (list)     : A JSON-based array of structured attachments, presented as a URL-encoded string.(default= ``[{'pretext': 'pre-hello', 'text': 'text-world'}]`` )
            blocks (list)          : A JSON-based array of structured blocks, presented as a URL-encoded string.(default= ``[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}]`` )
            icon_emoji (str)       : Emoji to use as the icon for this message. Overrides  ``icon_url`` . See `authorship <https://api.slack.com/methods/chat.postMessage#authorship>`_ here. Use with `bot tokens <https://api.slack.com/docs/token-types#granular_bot>`_ requires  ``chat:write.customize`` .(default= ``":chart_with_upwards_trend:"`` )
            icon_url (str)         : URL to an image to use as the icon for this message. See `authorship <https://api.slack.com/methods/chat.postMessage#authorship>`_ here. Use with `bot tokens <https://api.slack.com/docs/token-types#granular_bot>`_ requires  ``chat:write.customize`` .(default= ``"http://lorempixel.com/48/48"`` )
            link_names (bool)      : Find and link channel names and usernames.(default= ``True`` )
            mrkdwn (bool)          : Disable Slack markup parsing by setting to  ``False`` . Enabled by default.
            parse (str)            : Change how messages are treated. Defaults to  ``None`` . See `here <https://api.slack.com/methods/chat.postMessage#formatting>`_.(default= ``"full"`` )
            reply_broadcast (bool) : Used in conjunction with  ``thread_ts``  and indicates whether reply should be made visible to everyone in the channel or conversation. Defaults to  ``False`` .(default= ``True`` )
            thread_ts (float)      : Provide another message's  ``ts``  value to make this message a reply. Avoid using a reply's  ``ts``  value; use its parent instead.(default= ``1234567890.123456`` )
            unfurl_links (bool)    : Pass True to enable unfurling of primarily text-based content.(default= ``True`` )
            unfurl_media (bool)    : Pass False to disable unfurling of media content.
            username (str)         : Set your bot's user name. See `authorship <https://api.slack.com/methods/chat.postMessage#authorship>`_ here. Use with `bot tokens <https://api.slack.com/docs/token-types#granular_bot>`_ requires  ``chat:write.customize`` .(default= ``"My Bot"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_postMessage(
            ...     channel="C1234567890",
            ...     text="Hello world",
            ...     as_user=True,
            ...     attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}],
            ...     blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}],
            ...     icon_emoji=":chart_with_upwards_trend:",
            ...     icon_url="http://lorempixel.com/48/48",
            ...     link_names=True,
            ...     mrkdwn=False,
            ...     parse="full",
            ...     reply_broadcast=True,
            ...     thread_ts=1234567890.123456,
            ...     unfurl_links=True,
            ...     unfurl_media=False,
            ...     username="My Bot",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.postMessage", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_scheduleMessage(self, channel, post_at, text, as_user=True, attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}], blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}], link_names=True, parse="full", reply_broadcast=True, thread_ts=1234567890.123456, unfurl_links=True, unfurl_media=False):
        """Schedules a message to be sent to a channel.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:user``, ``chat:write:bot`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            channel (str)          : Channel, private group, or DM channel to send message to. Can be an encoded ID, or a name. See `here <https://api.slack.com/methods/chat.scheduleMessage#channels>`_ for more details.(default= ``"C1234567890"`` )
            post_at (int)          : Unix EPOCH timestamp of time in future to send the message.(default= ``299876400`` )
            text (str)             : How this field works and whether it is required depends on other fields you use in your API call. `See here <https://api.slack.com/methods/chat.scheduleMessage#text_usage>`_ for more detail.(default= ``"Hello world"`` )
            as_user (bool)         : Pass True to post the message as the authed user, instead of as a bot. Defaults to False. See `chat.postMessage <https://api.slack.com/methods/chat.postMessage#authorship>`_.(default= ``True`` )
            attachments (list)     : A JSON-based array of structured attachments, presented as a URL-encoded string.(default= ``[{'pretext': 'pre-hello', 'text': 'text-world'}]`` )
            blocks (list)          : A JSON-based array of structured blocks, presented as a URL-encoded string.(default= ``[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}]`` )
            link_names (bool)      : Find and link channel names and usernames.(default= ``True`` )
            parse (str)            : Change how messages are treated. Defaults to  ``None`` . See `chat.postMessage <https://api.slack.com/methods/chat.postMessage#formatting>`_.(default= ``"full"`` )
            reply_broadcast (bool) : Used in conjunction with  ``thread_ts``  and indicates whether reply should be made visible to everyone in the channel or conversation. Defaults to  ``False`` .(default= ``True`` )
            thread_ts (float)      : Provide another message's  ``ts``  value to make this message a reply. Avoid using a reply's  ``ts``  value; use its parent instead.(default= ``1234567890.123456`` )
            unfurl_links (bool)    : Pass True to enable unfurling of primarily text-based content.(default= ``True`` )
            unfurl_media (bool)    : Pass False to disable unfurling of media content.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_scheduleMessage(
            ...     channel="C1234567890",
            ...     post_at=299876400,
            ...     text="Hello world",
            ...     as_user=True,
            ...     attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}],
            ...     blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}],
            ...     link_names=True,
            ...     parse="full",
            ...     reply_broadcast=True,
            ...     thread_ts=1234567890.123456,
            ...     unfurl_links=True,
            ...     unfurl_media=False,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.scheduleMessage", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_unfurl(self, channel, ts, unfurls, user_auth_message=None, user_auth_required=True, user_auth_url="https://example.com/onboarding?user_id=xxx"):
        """Provide custom unfurl behavior for user-posted URLs
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``links:write``     |
        +--------------+---------------------+
        | user         | ``links:write``     |
        +--------------+---------------------+

        Args:
            channel (str)             : Channel ID of the message(default= ``"C1234567890"`` )
            ts (str)                  : Timestamp of the message to add unfurl behavior to.
            unfurls (str)             : URL-encoded JSON map with keys set to URLs featured in the the message, pointing to their unfurl blocks or message attachments.
            user_auth_message (str)   : Provide a simply-formatted string to send as an ephemeral message to the user as invitation to authenticate further and enable full unfurling behavior
            user_auth_required (bool) : Set to  ``True``  or  ``1``  to indicate the user must install your Slack app to trigger unfurls for this domain(default= ``True`` )
            user_auth_url (str)       : Send users to this custom URL where they will complete authentication in your app to fully trigger unfurling. Value should be properly URL-encoded.(default= ``"https://example.com/onboarding?user_id=xxx"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_unfurl(
            ...     channel="C1234567890",
            ...     ts=None,
            ...     unfurls=None,
            ...     user_auth_message=None,
            ...     user_auth_required=True,
            ...     user_auth_url="https://example.com/onboarding?user_id=xxx",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.unfurl", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_update(self, channel, ts, as_user=True, attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}], blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}], link_names=True, parse="none", text="Hello world"):
        """Updates a message.
        
        +--------------+---------------------------------------------------------+
        | Token type   | Required scope(s)                                       |
        +==============+=========================================================+
        | bot          | ``chat:write``                                          |
        +--------------+---------------------------------------------------------+
        | user         | ``chat:write``, ``chat:write:bot``, ``chat:write:user`` |
        +--------------+---------------------------------------------------------+
        | classic bot  | ``bot``                                                 |
        +--------------+---------------------------------------------------------+

        Args:
            channel (str)      : Channel containing the message to be updated.(default= ``"C1234567890"`` )
            ts (float)         : Timestamp of the message to be updated.(default= ``1405894322.002768`` )
            as_user (bool)     : Pass True to update the message as the authed user. `Bot users <https://api.slack.com/bot-users>`_ in this context are considered authed users.(default= ``True`` )
            attachments (list) : A JSON-based array of structured attachments, presented as a URL-encoded string. This field is required when not presenting  ``text`` . If you don't include this field, the message's previous  ``attachments``  will be retained. To remove previous  ``attachments`` , include an empty array for this field.(default= ``[{'pretext': 'pre-hello', 'text': 'text-world'}]`` )
            blocks (list)      : A JSON-based array of `structured blocks <https://api.slack.com/block-kit/building>`_, presented as a URL-encoded string. If you don't include this field, the message's previous  ``blocks``  will be retained. To remove previous  ``blocks`` , include an empty array for this field.(default= ``[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}]`` )
            link_names (bool)  : Find and link channel names and usernames. Defaults to  ``None`` . If you do not specify a value for this field, the original value set for the message will be overwritten with the default,  ``None`` .(default= ``True`` )
            parse (str)        : Change how messages are treated. Defaults to  ``client`` , unlike  ``chat.postMessage`` . Accepts either  ``None``  or  ``full`` . If you do not specify a value for this field, the original value set for the message will be overwritten with the default,  ``client`` .(default= ``"none"`` )
            text (str)         : New text for the message, using the `default formatting rules <https://api.slack.com/reference/surfaces/formatting>`_. It's not required when presenting  ``blocks``  or  ``attachments`` .(default= ``"Hello world"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_update(
            ...     channel="C1234567890",
            ...     ts=1405894322.002768,
            ...     as_user=True,
            ...     attachments=[{'pretext': 'pre-hello', 'text': 'text-world'}],
            ...     blocks=[{'type': 'section', 'text': {'type': 'plain_text', 'text': 'Hello world'}}],
            ...     link_names=True,
            ...     parse="none",
            ...     text="Hello world",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.update", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def chat_scheduledMessages_list(self, channel="C123456789", cursor="dXNlcjpVMDYxTkZUVDI=", latest=1562137200, limit=100, oldest=1562137200, team_id="T1234567890"):
        """Returns a list of scheduled messages.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            channel (str) : The channel of the scheduled messages(default= ``"C123456789"`` )
            cursor (str)  : For pagination purposes, this is the  ``cursor``  value returned from a previous call to  ``chat.scheduledmessages.list``  indicating where you want to start this call from.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            latest (int)  : A UNIX timestamp of the latest value in the time range(default= ``1562137200`` )
            limit (int)   : Maximum number of original entries to return.(default= ``100`` )
            oldest (int)  : A UNIX timestamp of the oldest value in the time range(default= ``1562137200`` )
            team_id (str) : encoded team id to list channels in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.chat_scheduledMessages_list(
            ...     channel="C123456789",
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     latest=1562137200,
            ...     limit=100,
            ...     oldest=1562137200,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="chat.scheduledMessages.list", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_archive(self, channel):
        """Archives a conversation.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : ID of conversation to archive(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_archive(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.archive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_close(self, channel):
        """Closes a direct message or multi-person direct message.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+
        | classic bot  | ``bot``                                                             |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : Conversation to close.(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_close(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.close", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_create(self, name, is_private=True, team_id="T1234567890"):
        """Initiates a public or private channel-based conversation
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            name (str)        : Name of the public or private channel to create(default= ``"mychannel"`` )
            is_private (bool) : Create a private channel instead of a public one(default= ``True`` )
            team_id (str)     : encoded team id to create the channel in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_create(
            ...     name="mychannel",
            ...     is_private=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.create", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_history(self, channel, cursor="dXNlcjpVMDYxTkZUVDI=", inclusive=True, latest=1234567890.123456, limit=20, oldest=1234567890.123456):
        """Fetches a conversation's history of messages and events.
        
        +--------------+----------------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                          |
        +==============+============================================================================+
        | bot          | ``channels:history``, ``groups:history``, ``im:history``, ``mpim:history`` |
        +--------------+----------------------------------------------------------------------------+
        | user         | ``channels:history``, ``groups:history``, ``im:history``, ``mpim:history`` |
        +--------------+----------------------------------------------------------------------------+
        | classic bot  | ``bot``                                                                    |
        +--------------+----------------------------------------------------------------------------+

        Args:
            channel (str)    : Conversation ID to fetch history for.(default= ``"C1234567890"`` )
            cursor (str)     : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            inclusive (bool) : Include messages with latest or oldest timestamp in results only when either timestamp is specified.(default= ``True`` )
            latest (float)   : End of time range of messages to include in results.(default= ``1234567890.123456`` )
            limit (int)      : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the users list hasn't been reached.(default= ``20`` )
            oldest (float)   : Start of time range of messages to include in results.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_history(
            ...     channel="C1234567890",
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     inclusive=True,
            ...     latest=1234567890.123456,
            ...     limit=20,
            ...     oldest=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.history", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def conversations_info(self, channel, include_locale=True, include_num_members=True):
        """Retrieve information about a conversation.
        
        +--------------+----------------------------------------------------------------+
        | Token type   | Required scope(s)                                              |
        +==============+================================================================+
        | bot          | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | user         | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | classic bot  | ``bot``                                                        |
        +--------------+----------------------------------------------------------------+

        Args:
            channel (str)              : Conversation ID to learn more about(default= ``"C1234567890"`` )
            include_locale (bool)      : Set this to  ``True``  to receive the locale for this conversation. Defaults to  ``False`` (default= ``True`` )
            include_num_members (bool) : Set to  ``True``  to include the member count for the specified conversation. Defaults to  ``False`` (default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_info(
            ...     channel="C1234567890",
            ...     include_locale=True,
            ...     include_num_members=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def conversations_invite(self, channel, users):
        """Invites users to a channel.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : The ID of the public or private channel to invite user(s) to.(default= ``"C1234567890"`` )
            users (str)   : A comma separated list of user IDs. Up to 1000 users may be listed.(default= ``"W1234567890,U2345678901,U3456789012"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_invite(
            ...     channel="C1234567890",
            ...     users="W1234567890,U2345678901,U3456789012",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.invite", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_join(self, channel):
        """Joins an existing conversation.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:join``   |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str) : ID of conversation to join(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_join(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.join", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_kick(self, channel, user):
        """Removes a user from a conversation.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : ID of conversation to remove user from.(default= ``"C1234567890"`` )
            user (str)    : User ID to be removed.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_kick(
            ...     channel="C1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.kick", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_leave(self, channel):
        """Leaves a conversation.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : Conversation to leave(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_leave(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.leave", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", exclude_archived=True, limit=20, team_id="T1234567890", types="public_channel,private_channel"):
        """Lists all channels in a Slack team.
        
        +--------------+----------------------------------------------------------------+
        | Token type   | Required scope(s)                                              |
        +==============+================================================================+
        | bot          | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | user         | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | classic bot  | ``bot``                                                        |
        +--------------+----------------------------------------------------------------+

        Args:
            cursor (str)            : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            exclude_archived (bool) : Set to  ``True``  to exclude archived channels from the list(default= ``True`` )
            limit (int)             : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached. Must be an integer no larger than 1000.(default= ``20`` )
            team_id (str)           : encoded team id to list channels in, required if org token is used(default= ``"T1234567890"`` )
            types (str)             : Mix and match channel types by providing a comma-separated list of any combination of  ``public_channel`` ,  ``private_channel`` ,  ``mpim`` ,  ``im`` (default= ``"public_channel,private_channel"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     exclude_archived=True,
            ...     limit=20,
            ...     team_id="T1234567890",
            ...     types="public_channel,private_channel",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def conversations_mark(self, channel, ts):
        """Sets the read cursor in a channel.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+
        | classic bot  | ``bot``                                                             |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : Channel or conversation to set the read cursor for.(default= ``"C012345678"`` )
            ts (float)    : Unique identifier of message you want marked as most recently seen in this conversation.(default= ``1593473566.0002`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_mark(
            ...     channel="C012345678",
            ...     ts=1593473566.0002,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.mark", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_members(self, channel, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20):
        """Retrieve members of a conversation.
        
        +--------------+----------------------------------------------------------------+
        | Token type   | Required scope(s)                                              |
        +==============+================================================================+
        | bot          | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | user         | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | classic bot  | ``bot``                                                        |
        +--------------+----------------------------------------------------------------+

        Args:
            channel (str) : ID of the conversation to retrieve members for(default= ``"C1234567890"`` )
            cursor (str)  : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)   : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the users list hasn't been reached.(default= ``20`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_members(
            ...     channel="C1234567890",
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.members", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def conversations_open(self, channel="G1234567890", return_im=True, users="W1234567890,U2345678901,U3456789012"):
        """Opens or resumes a direct message or multi-person direct message.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+
        | classic bot  | ``bot``                                                             |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str)    : Resume a conversation by supplying an  ``im``  or  ``mpim`` 's ID. Or provide the  ``users``  field instead.(default= ``"G1234567890"`` )
            return_im (bool) : Boolean, indicates you want the full IM channel definition in the response.(default= ``True`` )
            users (str)      : Comma separated lists of users. If only one user is included, this creates a 1:1 DM.  The ordering of the users is preserved whenever a multi-person direct message is returned. Supply a  ``channel``  when not supplying  ``users`` .(default= ``"W1234567890,U2345678901,U3456789012"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_open(
            ...     channel="G1234567890",
            ...     return_im=True,
            ...     users="W1234567890,U2345678901,U3456789012",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.open", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_rename(self, channel, name):
        """Renames a conversation.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : ID of conversation to rename(default= ``"C1234567890"`` )
            name (str)    : New name for conversation.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_rename(
            ...     channel="C1234567890",
            ...     name=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.rename", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_replies(self, channel, ts, cursor="dXNlcjpVMDYxTkZUVDI=", inclusive=True, latest=1234567890.123456, limit=20, oldest=1234567890.123456):
        """Retrieve a thread of messages posted to a conversation
        
        +--------------+----------------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                          |
        +==============+============================================================================+
        | bot          | ``channels:history``, ``groups:history``, ``im:history``, ``mpim:history`` |
        +--------------+----------------------------------------------------------------------------+
        | user         | ``channels:history``, ``groups:history``, ``im:history``, ``mpim:history`` |
        +--------------+----------------------------------------------------------------------------+
        | classic bot  | ``bot``                                                                    |
        +--------------+----------------------------------------------------------------------------+

        Args:
            channel (str)    : Conversation ID to fetch thread from.(default= ``"C1234567890"`` )
            ts (float)       : Unique identifier of a thread's parent message.  ``ts``  must be the timestamp of an existing message with 0 or more replies. If there are no replies then just the single message referenced by  ``ts``  will return - it is just an ordinary, unthreaded message.(default= ``1234567890.123456`` )
            cursor (str)     : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            inclusive (bool) : Include messages with latest or oldest timestamp in results only when either timestamp is specified.(default= ``True`` )
            latest (float)   : End of time range of messages to include in results.(default= ``1234567890.123456`` )
            limit (int)      : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the users list hasn't been reached.(default= ``20`` )
            oldest (float)   : Start of time range of messages to include in results.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_replies(
            ...     channel="C1234567890",
            ...     ts=1234567890.123456,
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     inclusive=True,
            ...     latest=1234567890.123456,
            ...     limit=20,
            ...     oldest=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.replies", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def conversations_setPurpose(self, channel, purpose):
        """Sets the purpose for a conversation.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+
        | classic bot  | ``bot``                                                             |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : Conversation to set the purpose of(default= ``"C1234567890"`` )
            purpose (str) : A new, specialer purpose(default= ``"My More Special Purpose"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_setPurpose(
            ...     channel="C1234567890",
            ...     purpose="My More Special Purpose",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.setPurpose", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_setTopic(self, channel, topic):
        """Sets the topic for a conversation.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+
        | classic bot  | ``bot``                                                             |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : Conversation to set the topic of(default= ``"C1234567890"`` )
            topic (str)   : The new topic string. Does not support formatting or linkification.(default= ``"Apply topically for best effects"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_setTopic(
            ...     channel="C1234567890",
            ...     topic="Apply topically for best effects",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.setTopic", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def conversations_unarchive(self, channel):
        """Reverses conversation archival.
        
        +--------------+---------------------------------------------------------------------+
        | Token type   | Required scope(s)                                                   |
        +==============+=====================================================================+
        | bot          | ``channels:manage``, ``groups:write``, ``im:write``, ``mpim:write`` |
        +--------------+---------------------------------------------------------------------+
        | user         | ``channels:write``, ``groups:write``, ``im:write``, ``mpim:write``  |
        +--------------+---------------------------------------------------------------------+

        Args:
            channel (str) : ID of conversation to unarchive(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.conversations_unarchive(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="conversations.unarchive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def dialog_open(self, dialog, trigger_id):
        """Open a dialog with a user
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            dialog (str)     : The dialog definition. This must be a JSON-encoded string.
            trigger_id (str) : Exchange a trigger to post to the user.(default= ``"12345.98765.abcd2358fdea"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.dialog_open(
            ...     dialog=None,
            ...     trigger_id="12345.98765.abcd2358fdea",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="dialog.open", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def dnd_endDnd(self):
        """Ends the current user's Do Not Disturb session immediately.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``dnd:write``       |
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.dnd_endDnd(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="dnd.endDnd", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def dnd_endSnooze(self):
        """Ends the current user's snooze mode immediately.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``dnd:write``       |
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.dnd_endSnooze(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="dnd.endSnooze", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def dnd_info(self, user="U1234"):
        """Retrieves a user's current Do Not Disturb status.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``dnd:read``        |
        +--------------+---------------------+
        | user         | ``dnd:read``        |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            user (str) : User to fetch status for (defaults to current user)(default= ``"U1234"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.dnd_info(
            ...     user="U1234",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="dnd.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def dnd_setSnooze(self, num_minutes):
        """Turns on Do Not Disturb mode for the current user, or changes its duration.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``dnd:write``       |
        +--------------+---------------------+

        Args:
            num_minutes (int) : Number of minutes, from now, to snooze until.(default= ``60`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.dnd_setSnooze(
            ...     num_minutes=60,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="dnd.setSnooze", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def dnd_teamInfo(self, users):
        """Retrieves the Do Not Disturb status for up to 50 users on a team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``dnd:read``        |
        +--------------+---------------------+
        | user         | ``dnd:read``        |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            users (str) : Comma-separated list of users to fetch Do Not Disturb status for(default= ``"U1234,W4567"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.dnd_teamInfo(
            ...     users="U1234,W4567",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="dnd.teamInfo", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def emoji_list(self):
        """Lists custom emoji for a team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``emoji:read``      |
        +--------------+---------------------+
        | user         | ``emoji:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.emoji_list(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="emoji.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_comments_delete(self, file, id):
        """Deletes an existing comment on a file.
        
        +--------------+---------------------------------------+
        | Token type   | Required scope(s)                     |
        +==============+=======================================+
        | bot          | ``files:write``                       |
        +--------------+---------------------------------------+
        | user         | ``files:write``, ``files:write:user`` |
        +--------------+---------------------------------------+
        | classic bot  | ``bot``                               |
        +--------------+---------------------------------------+

        Args:
            file (str) : File to delete a comment from.(default= ``"F1234567890"`` )
            id (str)   : The comment to delete.(default= ``"Fc1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_comments_delete(
            ...     file="F1234567890",
            ...     id="Fc1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.comments.delete", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def files_delete(self, file):
        """Deletes a file.
        
        +--------------+---------------------------------------+
        | Token type   | Required scope(s)                     |
        +==============+=======================================+
        | bot          | ``files:write``                       |
        +--------------+---------------------------------------+
        | user         | ``files:write``, ``files:write:user`` |
        +--------------+---------------------------------------+
        | classic bot  | ``bot``                               |
        +--------------+---------------------------------------+

        Args:
            file (str) : ID of file to delete.(default= ``"F1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_delete(
            ...     file="F1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.delete", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def files_info(self, file, count=20, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20, page=2):
        """Gets information about a file.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``files:read``      |
        +--------------+---------------------+
        | user         | ``files:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            file (str)   : Specify a file by providing its ID.(default= ``"F2147483862"`` )
            count (int)  : Number of items to return per page.(default= ``20`` )
            cursor (str) : Parameter for pagination. File comments are paginated for a single file. Set  ``cursor``  equal to the  ``next_cursor``  attribute returned by the previous request's  ``response_metadata`` . This parameter is optional, but pagination is mandatory: the default value simply fetches the first "page" of the collection of comments. See `pagination <https://api.slack.com/docs/pagination>`_ for more details.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)  : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached.(default= ``20`` )
            page (int)   : Page number of results to return.(default= ``2`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_info(
            ...     file="F2147483862",
            ...     count=20,
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            ...     page=2,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_list(self, channel="C1234567890", count=20, page=2, show_files_hidden_by_limit=True, team_id="T1234567890", ts_from=123456789, ts_to=123456789, types="images", user="W1234567890"):
        """List for a team, in a channel, or from a user with applied filters.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``files:read``      |
        +--------------+---------------------+
        | user         | ``files:read``      |
        +--------------+---------------------+

        Args:
            channel (str)                     : Filter files appearing in a specific channel, indicated by its ID.(default= ``"C1234567890"`` )
            count (int)                       : Number of items to return per page.(default= ``20`` )
            page (int)                        : Page number of results to return.(default= ``2`` )
            show_files_hidden_by_limit (bool) : Show truncated file info for files hidden due to being too old, and the team who owns the file being over the file limit.(default= ``True`` )
            team_id (str)                     : encoded team id to list files in, required if org token is used(default= ``"T1234567890"`` )
            ts_from (int)                     : Filter files created after this timestamp (inclusive).(default= ``123456789`` )
            ts_to (int)                       : Filter files created before this timestamp (inclusive).(default= ``123456789`` )
            types (str)                       : Filter files by type (`see here <https://api.slack.com/methods/files.list#file_types>`_). You can pass multiple values in the types argument, like  ``types=spaces,snippets`` .The default value is  ``all`` , which does not filter the list.(default= ``"images"`` )
            user (str)                        : Filter files created by a single user.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_list(
            ...     channel="C1234567890",
            ...     count=20,
            ...     page=2,
            ...     show_files_hidden_by_limit=True,
            ...     team_id="T1234567890",
            ...     ts_from=123456789,
            ...     ts_to=123456789,
            ...     types="images",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_revokePublicURL(self, file):
        """Revokes public/external sharing access for a file
        
        +--------------+---------------------------------------+
        | Token type   | Required scope(s)                     |
        +==============+=======================================+
        | user         | ``files:write``, ``files:write:user`` |
        +--------------+---------------------------------------+

        Args:
            file (str) : File to revoke(default= ``"F1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_revokePublicURL(
            ...     file="F1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.revokePublicURL", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def files_sharedPublicURL(self, file):
        """Enables a file for public/external sharing.
        
        +--------------+---------------------------------------+
        | Token type   | Required scope(s)                     |
        +==============+=======================================+
        | user         | ``files:write``, ``files:write:user`` |
        +--------------+---------------------------------------+

        Args:
            file (str) : File to share(default= ``"F1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_sharedPublicURL(
            ...     file="F1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.sharedPublicURL", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def files_upload(self, channels="C1234567890", content="...", file="...", filename="foo.txt", filetype="php", initial_comment="Best!", thread_ts=1234567890.123456, title="My File"):
        """Uploads or creates a file.
        
        +--------------+---------------------------------------+
        | Token type   | Required scope(s)                     |
        +==============+=======================================+
        | bot          | ``files:write``                       |
        +--------------+---------------------------------------+
        | user         | ``files:write``, ``files:write:user`` |
        +--------------+---------------------------------------+
        | classic bot  | ``bot``                               |
        +--------------+---------------------------------------+

        Args:
            channels (str)        : Comma-separated list of channel names or IDs where the file will be shared.(default= ``"C1234567890"`` )
            content (ellipsis)    : File contents via a POST variable. If omitting this parameter, you must provide a  ``file`` .(default= ``"..."`` )
            file (ellipsis)       : File contents via  ``multipart/form-data`` . If omitting this parameter, you must submit  ``content`` .(default= ``"..."`` )
            filename (str)        : Filename of file.(default= ``"foo.txt"`` )
            filetype (str)        : A `file type <https://api.slack.com/types/file#file_types>`_ identifier.(default= ``"php"`` )
            initial_comment (str) : The message text introducing the file in specified  ``channels`` .(default= ``"Best!"`` )
            thread_ts (float)     : Provide another message's  ``ts``  value to upload this file as a reply. Never use a reply's  ``ts``  value; use its parent instead.(default= ``1234567890.123456`` )
            title (str)           : Title of file.(default= ``"My File"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_upload(
            ...     channels="C1234567890",
            ...     content="...",
            ...     file="...",
            ...     filename="foo.txt",
            ...     filetype="php",
            ...     initial_comment="Best!",
            ...     thread_ts=1234567890.123456,
            ...     title="My File",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.upload", 
            http_method="POST", 
            content_types=['multipart/form-data', 'application/x-www-form-urlencoded'],
            **params,        
        )

    def files_remote_add(self, external_id, external_url, title, filetype="doc", indexable_file_contents="...", preview_image="..."):
        """Adds a file from a remote service
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | bot          | ``remote_files:write`` |
        +--------------+------------------------+
        | classic bot  | ``bot``                |
        +--------------+------------------------+

        Args:
            external_id (int)                  : Creator defined GUID for the file.(default= ``123456`` )
            external_url (str)                 : URL of the remote file.(default= ``"http://example.com/my_cloud_service_file/abc123"`` )
            title (str)                        : Title of the file being shared.(default= ``"Danger, High Voltage!"`` )
            filetype (str)                     : type of file(default= ``"doc"`` )
            indexable_file_contents (ellipsis) : A text file (txt, pdf, doc, etc.) containing textual search terms that are used to improve discovery of the remote file.(default= ``"..."`` )
            preview_image (ellipsis)           : Preview of the document via  ``multipart/form-data`` .(default= ``"..."`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_remote_add(
            ...     external_id=123456,
            ...     external_url="http://example.com/my_cloud_service_file/abc123",
            ...     title="Danger, High Voltage!",
            ...     filetype="doc",
            ...     indexable_file_contents="...",
            ...     preview_image="...",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.remote.add", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_remote_info(self, external_id=123456, file="F2147483862"):
        """Retrieve information about a remote file added to Slack
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``remote_files:read`` |
        +--------------+-----------------------+
        | user         | ``remote_files:read`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            external_id (int) : Creator defined GUID for the file.(default= ``123456`` )
            file (str)        : Specify a file by providing its ID.(default= ``"F2147483862"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_remote_info(
            ...     external_id=123456,
            ...     file="F2147483862",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.remote.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_remote_list(self, channel="C1234567890", cursor="dXNlcjpVMDYxTkZUVDI=", limit=20, ts_from=123456789, ts_to=123456789):
        """Retrieve information about a remote file added to Slack
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``remote_files:read`` |
        +--------------+-----------------------+
        | user         | ``remote_files:read`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            channel (str) : Filter files appearing in a specific channel, indicated by its ID.(default= ``"C1234567890"`` )
            cursor (str)  : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)   : The maximum number of items to return.(default= ``20`` )
            ts_from (int) : Filter files created after this timestamp (inclusive).(default= ``123456789`` )
            ts_to (int)   : Filter files created before this timestamp (inclusive).(default= ``123456789`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_remote_list(
            ...     channel="C1234567890",
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            ...     ts_from=123456789,
            ...     ts_to=123456789,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.remote.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_remote_remove(self, external_id=123456, file="F2147483862"):
        """Remove a remote file.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | bot          | ``remote_files:write`` |
        +--------------+------------------------+
        | classic bot  | ``bot``                |
        +--------------+------------------------+

        Args:
            external_id (int) : Creator defined GUID for the file.(default= ``123456`` )
            file (str)        : Specify a file by providing its ID.(default= ``"F2147483862"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_remote_remove(
            ...     external_id=123456,
            ...     file="F2147483862",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.remote.remove", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_remote_share(self, channels, external_id=123456, file="F2147483862"):
        """Share a remote file into a channel.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | bot          | ``remote_files:share`` |
        +--------------+------------------------+
        | user         | ``remote_files:share`` |
        +--------------+------------------------+
        | classic bot  | ``bot``                |
        +--------------+------------------------+

        Args:
            channels (str)    : Comma-separated list of channel IDs where the file will be shared.(default= ``"C1234567890"`` )
            external_id (int) : The globally unique identifier (GUID) for the file, as set by the app registering the file with Slack.  Either this field or  ``file``  or both are required.(default= ``123456`` )
            file (str)        : Specify a file registered with Slack by providing its ID. Either this field or  ``external_id``  or both are required.(default= ``"F2147483862"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_remote_share(
            ...     channels="C1234567890",
            ...     external_id=123456,
            ...     file="F2147483862",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.remote.share", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def files_remote_update(self, external_id=123456, external_url="http://example.com/my_cloud_service_file/abc123", file="F2147483862", filetype="doc", indexable_file_contents="...", preview_image="...", title="Danger, High Voltage!"):
        """Updates an existing remote file.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | bot          | ``remote_files:write`` |
        +--------------+------------------------+
        | classic bot  | ``bot``                |
        +--------------+------------------------+

        Args:
            external_id (int)                  : Creator defined GUID for the file.(default= ``123456`` )
            external_url (str)                 : URL of the remote file.(default= ``"http://example.com/my_cloud_service_file/abc123"`` )
            file (str)                         : Specify a file by providing its ID.(default= ``"F2147483862"`` )
            filetype (str)                     : type of file(default= ``"doc"`` )
            indexable_file_contents (ellipsis) : File containing contents that can be used to improve searchability for the remote file.(default= ``"..."`` )
            preview_image (ellipsis)           : Preview of the document via  ``multipart/form-data`` .(default= ``"..."`` )
            title (str)                        : Title of the file being shared.(default= ``"Danger, High Voltage!"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.files_remote_update(
            ...     external_id=123456,
            ...     external_url="http://example.com/my_cloud_service_file/abc123",
            ...     file="F2147483862",
            ...     filetype="doc",
            ...     indexable_file_contents="...",
            ...     preview_image="...",
            ...     title="Danger, High Voltage!",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="files.remote.update", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def migration_exchange(self, users, team_id="T1234567890", to_old=True):
        """For Enterprise Grid workspaces, map local user IDs to global user IDs
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``tokens.basic``    |
        +--------------+---------------------+
        | user         | ``tokens.basic``    |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            users (str)   : A comma-separated list of user ids, up to 400 per request
            team_id (str) : Specify team_id starts with  ``T``  in case of Org Token(default= ``"T1234567890"`` )
            to_old (bool) : Specify  ``True``  to convert  ``W``  global user IDs to workspace-specific  ``U``  IDs. Defaults to  ``False`` .(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.migration_exchange(
            ...     users=None,
            ...     team_id="T1234567890",
            ...     to_old=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="migration.exchange", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def oauth_access(self, client_secret="33fea0113f5b1", code="ccdaa72ad", redirect_uri="http://example.com", single_channel=True):
        """Exchanges a temporary OAuth verifier code for an access token.
        

        Args:
            client_secret (str)   : Issued when you created your application.(default= ``"33fea0113f5b1"`` )
            code (str)            : The  ``code``  param returned via the OAuth callback.(default= ``"ccdaa72ad"`` )
            redirect_uri (str)    : This must match the originally submitted URI (if one was sent).(default= ``"http://example.com"`` )
            single_channel (bool) : Request the user to add your app only to a single channel. Only valid with a `legacy workspace app <https://api.slack.com/legacy-workspace-apps>`_.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.oauth_access(
            ...     client_secret="33fea0113f5b1",
            ...     code="ccdaa72ad",
            ...     redirect_uri="http://example.com",
            ...     single_channel=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="oauth.access", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def oauth_token(self, client_secret, code, redirect_uri="http://example.com", single_channel=True):
        """Exchanges a temporary OAuth verifier code for a workspace token.
        

        Args:
            client_secret (str)   : Issued when you created your application.(default= ``"33fea0113f5b1"`` )
            code (str)            : The  ``code``  param returned via the OAuth callback.(default= ``"ccdaa72ad"`` )
            redirect_uri (str)    : This must match the originally submitted URI (if one was sent).(default= ``"http://example.com"`` )
            single_channel (bool) : Request the user to add your app only to a single channel.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.oauth_token(
            ...     client_secret="33fea0113f5b1",
            ...     code="ccdaa72ad",
            ...     redirect_uri="http://example.com",
            ...     single_channel=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="oauth.token", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def oauth_v2_access(self, client_id="4b39e9-752c4", client_secret="33fea0113f5b1", redirect_uri="http://example.com"):
        """Exchanges a temporary OAuth verifier code for an access token.
        

        Args:
            client_id (str)     : Issued when you created your application.(default= ``"4b39e9-752c4"`` )
            client_secret (str) : Issued when you created your application.(default= ``"33fea0113f5b1"`` )
            redirect_uri (str)  : This must match the originally submitted URI (if one was sent).(default= ``"http://example.com"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.oauth_v2_access(
            ...     client_id="4b39e9-752c4",
            ...     client_secret="33fea0113f5b1",
            ...     redirect_uri="http://example.com",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="oauth.v2.access", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def pins_add(self, channel, timestamp=1234567890.123456):
        """Pins an item to a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``pins:write``      |
        +--------------+---------------------+
        | user         | ``pins:write``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)     : Channel to pin the item in.(default= ``"C1234567890"`` )
            timestamp (float) : Timestamp of the message to pin.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.pins_add(
            ...     channel="C1234567890",
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="pins.add", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def pins_list(self, channel):
        """Lists items pinned to a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``pins:read``       |
        +--------------+---------------------+
        | user         | ``pins:read``       |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to get pinned items for.(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.pins_list(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="pins.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def pins_remove(self, channel, timestamp=1234567890.123456):
        """Un-pins an item from a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``pins:write``      |
        +--------------+---------------------+
        | user         | ``pins:write``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)     : Channel where the item is pinned to.(default= ``"C1234567890"`` )
            timestamp (float) : Timestamp of the message to un-pin.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.pins_remove(
            ...     channel="C1234567890",
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="pins.remove", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def reactions_add(self, channel, name, timestamp):
        """Adds a reaction to an item.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``reactions:write`` |
        +--------------+---------------------+
        | user         | ``reactions:write`` |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)     : Channel where the message to add reaction to was posted.(default= ``"C1234567890"`` )
            name (str)        : Reaction (emoji) name.(default= ``"thumbsup"`` )
            timestamp (float) : Timestamp of the message to add reaction to.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reactions_add(
            ...     channel="C1234567890",
            ...     name="thumbsup",
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reactions.add", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def reactions_get(self, channel="C1234567890", file="F1234567890", file_comment="Fc1234567890", full=True, timestamp=1234567890.123456):
        """Gets reactions for an item.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``reactions:read``  |
        +--------------+---------------------+
        | user         | ``reactions:read``  |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)      : Channel where the message to get reactions for was posted.(default= ``"C1234567890"`` )
            file (str)         : File to get reactions for.(default= ``"F1234567890"`` )
            file_comment (str) : File comment to get reactions for.(default= ``"Fc1234567890"`` )
            full (bool)        : If True always return the complete reaction list.(default= ``True`` )
            timestamp (float)  : Timestamp of the message to get reactions for.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reactions_get(
            ...     channel="C1234567890",
            ...     file="F1234567890",
            ...     file_comment="Fc1234567890",
            ...     full=True,
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reactions.get", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def reactions_list(self, count=20, cursor="dXNlcjpVMDYxTkZUVDI=", full=True, limit=20, page=2, team_id="T1234567890", user="W1234567890"):
        """Lists reactions made by a user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``reactions:read``  |
        +--------------+---------------------+
        | user         | ``reactions:read``  |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            count (int)   : Number of items to return per page.(default= ``20`` )
            cursor (str)  : Parameter for pagination. Set  ``cursor``  equal to the  ``next_cursor``  attribute returned by the previous request's  ``response_metadata`` . This parameter is optional, but pagination is mandatory: the default value simply fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more details.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            full (bool)   : If True always return the complete reaction list.(default= ``True`` )
            limit (int)   : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached.(default= ``20`` )
            page (int)    : Page number of results to return.(default= ``2`` )
            team_id (str) : encoded team id to list reactions in, required if org token is used(default= ``"T1234567890"`` )
            user (str)    : Show reactions made by this user. Defaults to the authed user.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reactions_list(
            ...     count=20,
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     full=True,
            ...     limit=20,
            ...     page=2,
            ...     team_id="T1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reactions.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def reactions_remove(self, name, channel="C1234567890", file="F1234567890", file_comment="Fc1234567890", timestamp=1234567890.123456):
        """Removes a reaction from an item.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``reactions:write`` |
        +--------------+---------------------+
        | user         | ``reactions:write`` |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            name (str)         : Reaction (emoji) name.(default= ``"thumbsup"`` )
            channel (str)      : Channel where the message to remove reaction from was posted.(default= ``"C1234567890"`` )
            file (str)         : File to remove reaction from.(default= ``"F1234567890"`` )
            file_comment (str) : File comment to remove reaction from.(default= ``"Fc1234567890"`` )
            timestamp (float)  : Timestamp of the message to remove reaction from.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reactions_remove(
            ...     name="thumbsup",
            ...     channel="C1234567890",
            ...     file="F1234567890",
            ...     file_comment="Fc1234567890",
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reactions.remove", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def reminders_add(self, text, time, user="U18888888"):
        """Creates a reminder.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``reminders:write`` |
        +--------------+---------------------+

        Args:
            text (str) : The content of the reminder(default= ``"eat a banana"`` )
            time (int) : When this reminder should happen: the Unix timestamp (up to five years from now), the number of seconds until the reminder (if within 24 hours), or a natural language description (Ex. "in 15 minutes," or "every Thursday")(default= ``1602288000`` )
            user (str) : The user who will receive the reminder. If no user is specified, the reminder will go to user who created it.(default= ``"U18888888"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reminders_add(
            ...     text="eat a banana",
            ...     time=1602288000,
            ...     user="U18888888",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reminders.add", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def reminders_complete(self, reminder):
        """Marks a reminder as complete.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``reminders:write`` |
        +--------------+---------------------+

        Args:
            reminder (str) : The ID of the reminder to be marked as complete(default= ``"Rm12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reminders_complete(
            ...     reminder="Rm12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reminders.complete", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def reminders_delete(self, reminder):
        """Deletes a reminder.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``reminders:write`` |
        +--------------+---------------------+

        Args:
            reminder (str) : The ID of the reminder(default= ``"Rm12345678"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reminders_delete(
            ...     reminder="Rm12345678",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reminders.delete", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def reminders_info(self, reminder):
        """Gets information about a reminder.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``reminders:read``  |
        +--------------+---------------------+

        Args:
            reminder (str) : The ID of the reminder(default= ``"Rm23456789"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reminders_info(
            ...     reminder="Rm23456789",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reminders.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def reminders_list(self):
        """Lists all reminders created by or for a given user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``reminders:read``  |
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.reminders_list(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="reminders.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def rtm_connect(self, batch_presence_aware=1, presence_sub=True):
        """Starts a Real Time Messaging session.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``client``          |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            batch_presence_aware (int) : Batch presence deliveries via subscription. Enabling changes the shape of  ``presence_change``  events. See `batch presence <https://api.slack.com/docs/presence-and-status#batching>`_.(default= ``1`` )
            presence_sub (bool)        : Only deliver presence events when requested by subscription. See `presence subscriptions <https://api.slack.com/docs/presence-and-status#subscriptions>`_.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.rtm_connect(
            ...     batch_presence_aware=1,
            ...     presence_sub=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="rtm.connect", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def rtm_start(self, batch_presence_aware=1, include_locale=True, mpim_aware=True, no_latest=1, no_unreads=True, presence_sub=True, simple_latest=True):
        """Starts a Real Time Messaging session.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``client``          |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            batch_presence_aware (int) : Batch presence deliveries via subscription. Enabling changes the shape of  ``presence_change``  events. See `batch presence <https://api.slack.com/docs/presence-and-status#batching>`_.(default= ``1`` )
            include_locale (bool)      : Set this to  ``True``  to receive the locale for users and channels. Defaults to  ``False`` (default= ``True`` )
            mpim_aware (bool)          : Returns MPIMs to the client in the API response.(default= ``True`` )
            no_latest (int)            : Exclude latest timestamps for channels, groups, mpims, and ims. Automatically sets  ``no_unreads``  to  ``1`` (default= ``1`` )
            no_unreads (bool)          : Skip unread counts for each channel (improves performance).(default= ``True`` )
            presence_sub (bool)        : Only deliver presence events when requested by subscription. See `presence subscriptions <https://api.slack.com/docs/presence-and-status#subscriptions>`_.(default= ``True`` )
            simple_latest (bool)       : Return timestamp only for latest message object of each channel (improves performance).(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.rtm_start(
            ...     batch_presence_aware=1,
            ...     include_locale=True,
            ...     mpim_aware=True,
            ...     no_latest=1,
            ...     no_unreads=True,
            ...     presence_sub=True,
            ...     simple_latest=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="rtm.start", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def search_all(self, query, count=20, highlight=True, page=2, sort="timestamp", sort_dir="asc", team_id="T1234567890"):
        """Searches for messages and files matching a query.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``search:read``     |
        +--------------+---------------------+

        Args:
            query (str)      : Search query. May contains booleans, etc.(default= ``"pickleface"`` )
            count (int)      : Number of items to return per page.(default= ``20`` )
            highlight (bool) : Pass a value of  ``True``  to enable query highlight markers (see here).(default= ``True`` )
            page (int)       : Page number of results to return.(default= ``2`` )
            sort (str)       : Return matches sorted by either  ``score``  or  ``timestamp`` .(default= ``"timestamp"`` )
            sort_dir (str)   : Change sort direction to ascending ( ``asc`` ) or descending ( ``desc`` ).(default= ``"asc"`` )
            team_id (str)    : encoded team id to search in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.search_all(
            ...     query="pickleface",
            ...     count=20,
            ...     highlight=True,
            ...     page=2,
            ...     sort="timestamp",
            ...     sort_dir="asc",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="search.all", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def search_files(self, query, count=20, highlight=True, page=2, sort="timestamp", sort_dir="asc", team_id="T1234567890"):
        """Searches for files matching a query.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``search:read``     |
        +--------------+---------------------+

        Args:
            query (str)      : Search query.(default= ``"pickleface"`` )
            count (int)      : Number of items to return per page.(default= ``20`` )
            highlight (bool) : Pass a value of  ``True``  to enable query highlight markers (see here).(default= ``True`` )
            page (int)       : Page number of results to return.(default= ``2`` )
            sort (str)       : Return matches sorted by either  ``score``  or  ``timestamp`` .(default= ``"timestamp"`` )
            sort_dir (str)   : Change sort direction to ascending ( ``asc`` ) or descending ( ``desc`` ).(default= ``"asc"`` )
            team_id (str)    : encoded team id to search in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.search_files(
            ...     query="pickleface",
            ...     count=20,
            ...     highlight=True,
            ...     page=2,
            ...     sort="timestamp",
            ...     sort_dir="asc",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="search.files", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def search_messages(self, query, count=20, highlight=True, page=2, sort="timestamp", sort_dir="asc", team_id="T1234567890"):
        """Searches for messages matching a query.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``search:read``     |
        +--------------+---------------------+

        Args:
            query (str)      : Search query.(default= ``"pickleface"`` )
            count (int)      : Number of items to return per page.(default= ``20`` )
            highlight (bool) : Pass a value of  ``True``  to enable query highlight markers (see here).(default= ``True`` )
            page (int)       : Page number of results to return.(default= ``2`` )
            sort (str)       : Return matches sorted by either  ``score``  or  ``timestamp`` .(default= ``"timestamp"`` )
            sort_dir (str)   : Change sort direction to ascending ( ``asc`` ) or descending ( ``desc`` ).(default= ``"asc"`` )
            team_id (str)    : encoded team id to search in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.search_messages(
            ...     query="pickleface",
            ...     count=20,
            ...     highlight=True,
            ...     page=2,
            ...     sort="timestamp",
            ...     sort_dir="asc",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="search.messages", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def stars_add(self, channel="C1234567890", file="F1234567890", file_comment="Fc1234567890", timestamp=1234567890.123456):
        """Adds a star to an item.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``stars:write``     |
        +--------------+---------------------+
        | user         | ``stars:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)      : Channel to add star to, or channel where the message to add star to was posted (used with  ``timestamp`` ).(default= ``"C1234567890"`` )
            file (str)         : File to add star to.(default= ``"F1234567890"`` )
            file_comment (str) : File comment to add star to.(default= ``"Fc1234567890"`` )
            timestamp (float)  : Timestamp of the message to add star to.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.stars_add(
            ...     channel="C1234567890",
            ...     file="F1234567890",
            ...     file_comment="Fc1234567890",
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="stars.add", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def stars_list(self, count=20, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20, page=2):
        """Lists stars for a user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``stars:read``      |
        +--------------+---------------------+

        Args:
            count (int)  : Number of items to return per page.(default= ``20`` )
            cursor (str) : Parameter for pagination. Set  ``cursor``  equal to the  ``next_cursor``  attribute returned by the previous request's  ``response_metadata`` . This parameter is optional, but pagination is mandatory: the default value simply fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more details.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)  : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached.(default= ``20`` )
            page (int)   : Page number of results to return.(default= ``2`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.stars_list(
            ...     count=20,
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            ...     page=2,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="stars.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def stars_remove(self, channel="C1234567890", file="F1234567890", file_comment="Fc1234567890", timestamp=1234567890.123456):
        """Removes a star from an item.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``stars:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)      : Channel to remove star from, or channel where the message to remove star from was posted (used with  ``timestamp`` ).(default= ``"C1234567890"`` )
            file (str)         : File to remove star from.(default= ``"F1234567890"`` )
            file_comment (str) : File comment to remove star from.(default= ``"Fc1234567890"`` )
            timestamp (float)  : Timestamp of the message to remove star from.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.stars_remove(
            ...     channel="C1234567890",
            ...     file="F1234567890",
            ...     file_comment="Fc1234567890",
            ...     timestamp=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="stars.remove", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def team_accessLogs(self, before=1457989166, count=20, page=2, team_id="T1234567890"):
        """Gets the access logs for the current team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``admin``           |
        +--------------+---------------------+

        Args:
            before (int)  : End of time range of logs to include in results (inclusive).(default= ``1457989166`` )
            count (int)   : Number of items to return per page.(default= ``20`` )
            page (int)    : Page number of results to return.(default= ``2`` )
            team_id (str) : encoded team id to get logs from, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.team_accessLogs(
            ...     before=1457989166,
            ...     count=20,
            ...     page=2,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="team.accessLogs", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def team_billableInfo(self, team_id="T1234567890", user="W1234567890"):
        """Gets billable users information for the current team.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | user         | ``No scope required`` |
        +--------------+-----------------------+

        Args:
            team_id (str) : encoded team id to get the billable information from, required if org token is used(default= ``"T1234567890"`` )
            user (str)    : A user to retrieve the billable information for. Defaults to all users.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.team_billableInfo(
            ...     team_id="T1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="team.billableInfo", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def team_info(self, team="T1234567890"):
        """Gets information about the current team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``team:read``       |
        +--------------+---------------------+
        | user         | ``team:read``       |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            team (str) : Team to get info on, if omitted, will return information about the current team. Will only return team that the authenticated token is allowed to see through external shared channels(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.team_info(
            ...     team="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="team.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def team_integrationLogs(self, app_id=None, change_type="added", count=20, page=2, service_id=None, team_id="T1234567890", user="W1234567890"):
        """Gets the integration logs for the current team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``admin``           |
        +--------------+---------------------+

        Args:
            app_id (str)      : Filter logs to this Slack app. Defaults to all logs.
            change_type (str) : Filter logs with this change type. Defaults to all logs.(default= ``"added"`` )
            count (int)       : Number of items to return per page.(default= ``20`` )
            page (int)        : Page number of results to return.(default= ``2`` )
            service_id (str)  : Filter logs to this service. Defaults to all logs.
            team_id (str)     : encoded team id to get logs from, required if org token is used(default= ``"T1234567890"`` )
            user (str)        : Filter logs generated by this userâ€™s actions. Defaults to all logs.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.team_integrationLogs(
            ...     app_id=None,
            ...     change_type="added",
            ...     count=20,
            ...     page=2,
            ...     service_id=None,
            ...     team_id="T1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="team.integrationLogs", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def team_profile_get(self, visibility="all"):
        """Retrieve a team's profile.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | bot          | ``users.profile:read`` |
        +--------------+------------------------+
        | user         | ``users.profile:read`` |
        +--------------+------------------------+

        Args:
            visibility (str) : Filter by visibility.(default= ``"all"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.team_profile_get(
            ...     visibility="all",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="team.profile.get", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def usergroups_create(self, name, channels="C1234567890", description=None, handle="marketing", include_count=True, team_id="T1234567890"):
        """Create a User Group
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``usergroups:write`` |
        +--------------+----------------------+
        | user         | ``usergroups:write`` |
        +--------------+----------------------+

        Args:
            name (str)           : A name for the User Group. Must be unique among User Groups.(default= ``"My Test Team"`` )
            channels (str)       : A comma separated string of encoded channel IDs for which the User Group uses as a default.(default= ``"C1234567890"`` )
            description (str)    : A short description of the User Group.
            handle (str)         : A mention handle. Must be unique among channels, users and User Groups.(default= ``"marketing"`` )
            include_count (bool) : Include the number of users in each User Group.(default= ``True`` )
            team_id (str)        : Encoded team id where the user group has to be created, required if org token is used.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_create(
            ...     name="My Test Team",
            ...     channels="C1234567890",
            ...     description=None,
            ...     handle="marketing",
            ...     include_count=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.create", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def usergroups_disable(self, usergroup, include_count=True, team_id="T1234567890"):
        """Disable an existing User Group
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``usergroups:write`` |
        +--------------+----------------------+
        | user         | ``usergroups:write`` |
        +--------------+----------------------+

        Args:
            usergroup (str)      : The encoded ID of the User Group to disable.(default= ``"S0604QSJC"`` )
            include_count (bool) : Include the number of users in the User Group.(default= ``True`` )
            team_id (str)        : Encoded team id where the user group is, required if org token is used.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_disable(
            ...     usergroup="S0604QSJC",
            ...     include_count=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.disable", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def usergroups_enable(self, usergroup, include_count=True, team_id="T1234567890"):
        """Enable a User Group
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``usergroups:write`` |
        +--------------+----------------------+
        | user         | ``usergroups:write`` |
        +--------------+----------------------+

        Args:
            usergroup (str)      : The encoded ID of the User Group to enable.(default= ``"S0604QSJC"`` )
            include_count (bool) : Include the number of users in the User Group.(default= ``True`` )
            team_id (str)        : Encoded team id where the user group is, required if org token is used.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_enable(
            ...     usergroup="S0604QSJC",
            ...     include_count=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.enable", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def usergroups_list(self, include_count=True, include_disabled=True, include_users=True, team_id="T1234567890"):
        """List all User Groups for a team
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``usergroups:read`` |
        +--------------+---------------------+
        | user         | ``usergroups:read`` |
        +--------------+---------------------+

        Args:
            include_count (bool)    : Include the number of users in each User Group.(default= ``True`` )
            include_disabled (bool) : Include disabled User Groups.(default= ``True`` )
            include_users (bool)    : Include the list of users for each User Group.(default= ``True`` )
            team_id (str)           : encoded team id to list user groups in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_list(
            ...     include_count=True,
            ...     include_disabled=True,
            ...     include_users=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def usergroups_update(self, usergroup, channels="C1234567890", description=None, handle="marketing", include_count=True, name="My Test Team", team_id="T1234567890"):
        """Update an existing User Group
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``usergroups:write`` |
        +--------------+----------------------+
        | user         | ``usergroups:write`` |
        +--------------+----------------------+

        Args:
            usergroup (str)      : The encoded ID of the User Group to update.(default= ``"S0604QSJC"`` )
            channels (str)       : A comma separated string of encoded channel IDs for which the User Group uses as a default.(default= ``"C1234567890"`` )
            description (str)    : A short description of the User Group.
            handle (str)         : A mention handle. Must be unique among channels, users and User Groups.(default= ``"marketing"`` )
            include_count (bool) : Include the number of users in the User Group.(default= ``True`` )
            name (str)           : A name for the User Group. Must be unique among User Groups.(default= ``"My Test Team"`` )
            team_id (str)        : encoded team id where the user group exists, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_update(
            ...     usergroup="S0604QSJC",
            ...     channels="C1234567890",
            ...     description=None,
            ...     handle="marketing",
            ...     include_count=True,
            ...     name="My Test Team",
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.update", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def usergroups_users_list(self, usergroup, include_disabled=True, team_id="T1234567890"):
        """List all users in a User Group
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``usergroups:read`` |
        +--------------+---------------------+
        | user         | ``usergroups:read`` |
        +--------------+---------------------+

        Args:
            usergroup (str)         : The encoded ID of the User Group to update.(default= ``"S0604QSJC"`` )
            include_disabled (bool) : Allow results that involve disabled User Groups.(default= ``True`` )
            team_id (str)           : encoded team id where the user group exists, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_users_list(
            ...     usergroup="S0604QSJC",
            ...     include_disabled=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.users.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def usergroups_users_update(self, usergroup, users, include_count=True, team_id="T1234567890"):
        """Update the list of users for a User Group
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``usergroups:write`` |
        +--------------+----------------------+
        | user         | ``usergroups:write`` |
        +--------------+----------------------+

        Args:
            usergroup (str)      : The encoded ID of the User Group to update.(default= ``"S0604QSJC"`` )
            users (str)          : A comma separated string of encoded user IDs that represent the entire list of users for the User Group.(default= ``"U060R4BJ4,U060RNRCZ"`` )
            include_count (bool) : Include the number of users in the User Group.(default= ``True`` )
            team_id (str)        : encoded team id where the user group exists, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.usergroups_users_update(
            ...     usergroup="S0604QSJC",
            ...     users="U060R4BJ4,U060RNRCZ",
            ...     include_count=True,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="usergroups.users.update", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def users_conversations(self, cursor="dXNlcjpVMDYxTkZUVDI=", exclude_archived=True, limit=20, team_id="T1234567890", types="im,mpim", user="W0B2345D"):
        """List conversations the calling user may access.
        
        +--------------+----------------------------------------------------------------+
        | Token type   | Required scope(s)                                              |
        +==============+================================================================+
        | bot          | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | user         | ``channels:read``, ``groups:read``, ``im:read``, ``mpim:read`` |
        +--------------+----------------------------------------------------------------+
        | classic bot  | ``bot``                                                        |
        +--------------+----------------------------------------------------------------+

        Args:
            cursor (str)            : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            exclude_archived (bool) : Set to  ``True``  to exclude archived channels from the list(default= ``True`` )
            limit (int)             : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached. Must be an integer no larger than 1000.(default= ``20`` )
            team_id (str)           : encoded team id to list conversations in, required if org token is used(default= ``"T1234567890"`` )
            types (str)             : Mix and match channel types by providing a comma-separated list of any combination of  ``public_channel`` ,  ``private_channel`` ,  ``mpim`` ,  ``im`` (default= ``"im,mpim"`` )
            user (str)              : Browse conversations by a specific user ID's membership. Non-public channels are restricted to those where the calling user shares membership.(default= ``"W0B2345D"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_conversations(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     exclude_archived=True,
            ...     limit=20,
            ...     team_id="T1234567890",
            ...     types="im,mpim",
            ...     user="W0B2345D",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.conversations", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_deletePhoto(self):
        """Delete the user profile photo
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | user         | ``users.profile:write`` |
        +--------------+-------------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_deletePhoto(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.deletePhoto", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_getPresence(self, user="W1234567890"):
        """Gets user presence information.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``users:read``      |
        +--------------+---------------------+
        | user         | ``users:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            user (str) : User to get presence info on. Defaults to the authed user.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_getPresence(
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.getPresence", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_identity(self):
        """Get a user's identity.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``identity.basic``  |
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_identity(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.identity", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_info(self, user, include_locale=True):
        """Gets information about a user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``users:read``      |
        +--------------+---------------------+
        | user         | ``users:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            user (str)            : User to get info on(default= ``"W1234567890"`` )
            include_locale (bool) : Set this to  ``True``  to receive the locale for this user. Defaults to  ``False`` (default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_info(
            ...     user="W1234567890",
            ...     include_locale=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", include_locale=True, limit=20, team_id="T1234567890"):
        """Lists all users in a Slack team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``users:read``      |
        +--------------+---------------------+
        | user         | ``users:read``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            cursor (str)          : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            include_locale (bool) : Set this to  ``True``  to receive the locale for users. Defaults to  ``False`` (default= ``True`` )
            limit (int)           : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the users list hasn't been reached. Providing no  ``limit``  value will result in Slack attempting to deliver you the entire result set. If the collection is too large you may experience  ``limit_required``  or HTTP 500 errors.(default= ``20`` )
            team_id (str)         : encoded team id to list users in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     include_locale=True,
            ...     limit=20,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_lookupByEmail(self, email):
        """Find a user with an email address.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``users:read.email`` |
        +--------------+----------------------+
        | user         | ``users:read.email`` |
        +--------------+----------------------+
        | classic bot  | ``bot``              |
        +--------------+----------------------+

        Args:
            email (str) : An email address belonging to a user in the workspace(default= ``"spengler@ghostbusters.example.com"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_lookupByEmail(
            ...     email="spengler@ghostbusters.example.com",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.lookupByEmail", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_setActive(self):
        """Marked a user as active. Deprecated and non-functional.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``users:write``     |
        +--------------+---------------------+
        | user         | ``users:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_setActive(
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.setActive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def users_setPhoto(self, crop_w=100, crop_x=10, crop_y=15, image="..."):
        """Set the user profile photo
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | user         | ``users.profile:write`` |
        +--------------+-------------------------+

        Args:
            crop_w (int)     : Width/height of crop box (always square)(default= ``100`` )
            crop_x (int)     : X coordinate of top-left corner of crop box(default= ``10`` )
            crop_y (int)     : Y coordinate of top-left corner of crop box(default= ``15`` )
            image (ellipsis) : File contents via  ``multipart/form-data`` .(default= ``"..."`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_setPhoto(
            ...     crop_w=100,
            ...     crop_x=10,
            ...     crop_y=15,
            ...     image="...",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.setPhoto", 
            http_method="POST", 
            content_types=['multipart/form-data', 'application/x-www-form-urlencoded'],
            **params,        
        )

    def users_setPresence(self, presence):
        """Manually sets user presence.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``users:write``     |
        +--------------+---------------------+
        | user         | ``users:write``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            presence (str) : Either  ``auto``  or  ``away`` (default= ``"away"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_setPresence(
            ...     presence="away",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.setPresence", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def users_profile_get(self, include_labels=True, user="W1234567890"):
        """Retrieve a user's profile information, including their custom status.
        
        +--------------+------------------------+
        | Token type   | Required scope(s)      |
        +==============+========================+
        | bot          | ``users.profile:read`` |
        +--------------+------------------------+
        | user         | ``users.profile:read`` |
        +--------------+------------------------+

        Args:
            include_labels (bool) : Include labels for each ID in custom profile fields. Using this parameter will heavily rate-limit your requests and is not recommended.(default= ``True`` )
            user (str)            : User to retrieve profile info for(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_profile_get(
            ...     include_labels=True,
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.profile.get", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def users_profile_set(self, name="first_name", profile={'first_name': 'John'}, user="W1234567890", value="John"):
        """Set a user's profile information, including custom status.
        
        +--------------+-------------------------+
        | Token type   | Required scope(s)       |
        +==============+=========================+
        | user         | ``users.profile:write`` |
        +--------------+-------------------------+

        Args:
            name (str)     : Name of a single key to set. Usable only if  ``profile``  is not passed.(default= ``"first_name"`` )
            profile (dict) : Collection of key:value pairs presented as a URL-encoded JSON hash. At most 50 fields may be set. Each field name is limited to 255 characters.(default= ``{'first_name': 'John'}`` )
            user (str)     : ID of user to change. This argument may only be specified by team admins on paid teams.(default= ``"W1234567890"`` )
            value (str)    : Value to set a single key to. Usable only if  ``profile``  is not passed.(default= ``"John"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.users_profile_set(
            ...     name="first_name",
            ...     profile={'first_name': 'John'},
            ...     user="W1234567890",
            ...     value="John",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="users.profile.set", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def views_open(self, trigger_id, view):
        """Open a view for a user.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            trigger_id (str) : Exchange a trigger to post to the user.(default= ``"12345.98765.abcd2358fdea"`` )
            view (str)       : A `view payload <https://api.slack.com/reference/surfaces/views>`_. This must be a JSON-encoded string.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.views_open(
            ...     trigger_id="12345.98765.abcd2358fdea",
            ...     view=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="views.open", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def views_publish(self, user_id, view, hash=156772938.1827394):
        """Publish a static view for a User.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            user_id (str) :  ``id``  of the user you want publish a view to.(default= ``"U0BPQUNTA"`` )
            view (str)    : A `view payload <https://api.slack.com/reference/surfaces/views>`_. This must be a JSON-encoded string.
            hash (float)  : A string that represents view state to protect against possible race conditions.(default= ``156772938.1827394`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.views_publish(
            ...     user_id="U0BPQUNTA",
            ...     view=None,
            ...     hash=156772938.1827394,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="views.publish", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def views_push(self, trigger_id, view):
        """Push a view onto the stack of a root view.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            trigger_id (str) : Exchange a trigger to post to the user.(default= ``"12345.98765.abcd2358fdea"`` )
            view (str)       : A `view payload <https://api.slack.com/reference/surfaces/views>`_. This must be a JSON-encoded string.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.views_push(
            ...     trigger_id="12345.98765.abcd2358fdea",
            ...     view=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="views.push", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def views_update(self, view, external_id="bmarley_view2", hash=156772938.1827394, view_id="VMM512F2U"):
        """Update an existing view.
        
        +--------------+-----------------------+
        | Token type   | Required scope(s)     |
        +==============+=======================+
        | bot          | ``No scope required`` |
        +--------------+-----------------------+
        | user         | ``No scope required`` |
        +--------------+-----------------------+
        | classic bot  | ``bot``               |
        +--------------+-----------------------+

        Args:
            view (str)        : A `view object <https://api.slack.com/reference/surfaces/views>`_. This must be a JSON-encoded string.
            external_id (str) : A unique identifier of the view set by the developer. Must be unique for all views on a team. Max length of 255 characters. Either  ``view_id``  or  ``external_id``  is required.(default= ``"bmarley_view2"`` )
            hash (float)      : A string that represents view state to protect against possible race conditions.(default= ``156772938.1827394`` )
            view_id (str)     : A unique identifier of the view to be updated. Either  ``view_id``  or  ``external_id``  is required.(default= ``"VMM512F2U"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.views_update(
            ...     view=None,
            ...     external_id="bmarley_view2",
            ...     hash=156772938.1827394,
            ...     view_id="VMM512F2U",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="views.update", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def workflows_stepCompleted(self, workflow_step_execute_id, outputs=None):
        """Indicate that an app's step in a workflow completed execution.
        
        +--------------+----------------------------+
        | Token type   | Required scope(s)          |
        +==============+============================+
        | bot          | ``workflow.steps:execute`` |
        +--------------+----------------------------+

        Args:
            workflow_step_execute_id (str) : Context identifier that maps to the correct workflow step execution.
            outputs (str)                  : Key-value object of outputs from your step. Keys of this object reflect the configured  ``key``  properties of your  ``outputs``  array from your  ``workflow_step``  object.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.workflows_stepCompleted(
            ...     workflow_step_execute_id=None,
            ...     outputs=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="workflows.stepCompleted", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def workflows_stepFailed(self, error, workflow_step_execute_id):
        """Indicate that an app's step in a workflow failed to execute.
        
        +--------------+----------------------------+
        | Token type   | Required scope(s)          |
        +==============+============================+
        | bot          | ``workflow.steps:execute`` |
        +--------------+----------------------------+

        Args:
            error (str)                    : A JSON-based object with a  ``message``  property that should contain a human readable error message.
            workflow_step_execute_id (str) : Context identifier that maps to the correct workflow step execution.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.workflows_stepFailed(
            ...     error=None,
            ...     workflow_step_execute_id=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="workflows.stepFailed", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def workflows_updateStep(self, workflow_step_edit_id, inputs={'title': {'value': 'The Title'}, 'submitter': {'value': '{{user}}'}}, outputs=[{'name': 'ticket_id', 'type': 'text', 'label': 'Ticket ID'}, {'name': 'title', 'type': 'text', 'label': 'Title'}], step_image_url=None, step_name=None):
        """Update the configuration for a workflow step.
        
        +--------------+----------------------------+
        | Token type   | Required scope(s)          |
        +==============+============================+
        | bot          | ``workflow.steps:execute`` |
        +--------------+----------------------------+

        Args:
            workflow_step_edit_id (str) : A context identifier provided with  ``view_submission``  payloads used to call back to  ``workflows.updateStep`` .
            inputs (dict)               : A JSON key-value map of inputs required from a user during configuration. This is the data your app expects to receive when the workflow step starts. **Please note** : the embedded variable format is set and replaced by the workflow system. You cannot create custom variables that will be replaced at runtime. `Read more about variables in workflow steps here <https://api.slack.com/workflows/steps#variables>`_.(default= ``{'title': {'value': 'The Title'}, 'submitter': {'value': '{{user}}'}}`` )
            outputs (list)              : An JSON array of output objects used during step execution. This is the data your app agrees to provide when your workflow step was executed.(default= ``[{'name': 'ticket_id', 'type': 'text', 'label': 'Ticket ID'}, {'name': 'title', 'type': 'text', 'label': 'Title'}]`` )
            step_image_url (str)        : An optional field that can be used to override app image that is shown in the Workflow Builder.
            step_name (str)             : An optional field that can be used to override the step name that is shown in the Workflow Builder.
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.workflows_updateStep(
            ...     workflow_step_edit_id=None,
            ...     inputs={'title': {'value': 'The Title'}, 'submitter': {'value': '{{user}}'}},
            ...     outputs=[{'name': 'ticket_id', 'type': 'text', 'label': 'Ticket ID'}, {'name': 'title', 'type': 'text', 'label': 'Title'}],
            ...     step_image_url=None,
            ...     step_name=None,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="workflows.updateStep", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def admin_conversations_whitelist_add(self, channel_id, group_id, team_id="T1234567890"):
        """Add an allowlist of IDP groups for accessing a channel
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to whitelist a group for.
            group_id (str)   : The `IDP Group <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_ ID to whitelist for the private channel.
            team_id (str)    : The workspace where the IDP Group and channel exist.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_whitelist_add(
            ...     channel_id=None,
            ...     group_id=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.whitelist.add", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_conversations_whitelist_listGroupsLinkedToChannel(self, channel_id, team_id="T1234567890"):
        """List all IDP Groups linked to a channel
        
        +--------------+------------------------------+
        | Token type   | Required scope(s)            |
        +==============+==============================+
        | user         | ``admin.conversations:read`` |
        +--------------+------------------------------+

        Args:
            channel_id (str) : 
            team_id (str)    : The workspace where the channele exists. This argument is required for channels only tied to one workspace, and optional for channels that are shared across an organization.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_whitelist_listGroupsLinkedToChannel(
            ...     channel_id=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.whitelist.listGroupsLinkedToChannel", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def admin_conversations_whitelist_remove(self, channel_id, group_id, team_id):
        """Remove an allowlisted IDP group linked to a private channel
        
        +--------------+-------------------------------+
        | Token type   | Required scope(s)             |
        +==============+===============================+
        | user         | ``admin.conversations:write`` |
        +--------------+-------------------------------+

        Args:
            channel_id (str) : The channel to remove a whitelisted group for.
            group_id (str)   : The `IDP Group <https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-Grid-org>`_ ID to remove from the private channel whitelist.
            team_id (str)    : The workspace where the IDP Group and channel exist.(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.admin_conversations_whitelist_remove(
            ...     channel_id=None,
            ...     group_id=None,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="admin.conversations.whitelist.remove", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def channels_archive(self, channel):
        """Archives a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to archive(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_archive(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.archive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_create(self, name, team_id="T1234567890", validate=True):
        """Creates a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            name (str)      : Name of channel to create(default= ``"mychannel"`` )
            team_id (str)   : encoded team id to create the channel in, required if org token is used(default= ``"T1234567890"`` )
            validate (bool) : Whether to return errors on invalid channel name instead of modifying it to meet the specified criteria.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_create(
            ...     name="mychannel",
            ...     team_id="T1234567890",
            ...     validate=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.create", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_history(self, channel, count=100, inclusive=True, latest=1234567890.123456, oldest=1234567890.123456, unreads=True):
        """Fetches history of messages and events from a channel.
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``channels:history`` |
        +--------------+----------------------+
        | user         | ``channels:history`` |
        +--------------+----------------------+
        | classic bot  | ``bot``              |
        +--------------+----------------------+

        Args:
            channel (str)    : Channel to fetch history for.(default= ``"C1234567890"`` )
            count (int)      : Number of messages to return, between 1 and 1000.(default= ``100`` )
            inclusive (bool) : Include messages with latest or oldest timestamp in results.(default= ``True`` )
            latest (float)   : End of time range of messages to include in results.(default= ``1234567890.123456`` )
            oldest (float)   : Start of time range of messages to include in results.(default= ``1234567890.123456`` )
            unreads (bool)   : Include  ``unread_count_display``  in the output?(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_history(
            ...     channel="C1234567890",
            ...     count=100,
            ...     inclusive=True,
            ...     latest=1234567890.123456,
            ...     oldest=1234567890.123456,
            ...     unreads=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.history", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def channels_info(self, channel, include_locale=True):
        """Gets information about a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:read``   |
        +--------------+---------------------+
        | user         | ``channels:read``   |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)         : Channel to get info on(default= ``"C1234567890"`` )
            include_locale (bool) : Set this to  ``True``  to receive the locale for this channel. Defaults to  ``False`` (default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_info(
            ...     channel="C1234567890",
            ...     include_locale=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def channels_invite(self, channel, user):
        """Invites a user to a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to invite user to.(default= ``"C1234567890"`` )
            user (str)    : User to invite to channel.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_invite(
            ...     channel="C1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.invite", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_join(self, name, team_id="T1234567890", validate=True):
        """Joins a channel, creating it if needed.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:join``   |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            name (str)      : Name of channel to join(default= ``"#general"`` )
            team_id (str)   : encoded team id to list channels in, required if org token is used(default= ``"T1234567890"`` )
            validate (bool) : Whether to return errors on invalid channel name instead of modifying it to meet the specified criteria.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_join(
            ...     name="#general",
            ...     team_id="T1234567890",
            ...     validate=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.join", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_kick(self, channel, user):
        """Removes a user from a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to remove user from.(default= ``"C1234567890"`` )
            user (str)    : User to remove from channel.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_kick(
            ...     channel="C1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.kick", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_leave(self, channel):
        """Leaves a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to leave(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_leave(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.leave", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", exclude_archived=True, exclude_members=True, limit=20, team_id="T1234567890"):
        """Lists all channels in a Slack team.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:read``   |
        +--------------+---------------------+
        | user         | ``channels:read``   |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            cursor (str)            : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            exclude_archived (bool) : Exclude archived channels from the list(default= ``True`` )
            exclude_members (bool)  : Exclude the  ``members``  collection from each  ``channel`` (default= ``True`` )
            limit (int)             : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the users list hasn't been reached.(default= ``20`` )
            team_id (str)           : encoded team id to list channels in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     exclude_archived=True,
            ...     exclude_members=True,
            ...     limit=20,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def channels_mark(self, channel, ts):
        """Sets the read cursor in a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Channel or conversation to set the read cursor for.(default= ``"C012345678"`` )
            ts (float)    : Unique identifier of message you want marked as most recently seen in this conversation.(default= ``1593473566.0002`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_mark(
            ...     channel="C012345678",
            ...     ts=1593473566.0002,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.mark", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_rename(self, channel, name, validate=True):
        """Renames a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str)   : Channel to rename(default= ``"C1234567890"`` )
            name (str)      : New name for channel.
            validate (bool) : Whether to return errors on invalid channel name instead of modifying it to meet the specified criteria.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_rename(
            ...     channel="C1234567890",
            ...     name=None,
            ...     validate=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.rename", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_replies(self, channel, thread_ts):
        """Retrieve a thread of messages posted to a channel
        
        +--------------+----------------------+
        | Token type   | Required scope(s)    |
        +==============+======================+
        | bot          | ``channels:history`` |
        +--------------+----------------------+
        | user         | ``channels:history`` |
        +--------------+----------------------+
        | classic bot  | ``bot``              |
        +--------------+----------------------+

        Args:
            channel (str)     : Channel to fetch thread from(default= ``"C1234567890"`` )
            thread_ts (float) : Unique identifier of a thread's parent message(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_replies(
            ...     channel="C1234567890",
            ...     thread_ts=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.replies", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def channels_setPurpose(self, channel, purpose, name_tagging=True):
        """Sets the purpose for a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)       : Channel to set the purpose of(default= ``"C1234567890"`` )
            purpose (str)       : The new purpose(default= ``"My Purpose"`` )
            name_tagging (bool) : if it is True, treat this like a message and not an unescaped thing(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_setPurpose(
            ...     channel="C1234567890",
            ...     purpose="My Purpose",
            ...     name_tagging=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.setPurpose", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_setTopic(self, channel, topic):
        """Sets the topic for a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``channels:manage`` |
        +--------------+---------------------+
        | user         | ``channels:write``  |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to set the topic of(default= ``"C1234567890"`` )
            topic (str)   : The new topic(default= ``"My Topic"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_setTopic(
            ...     channel="C1234567890",
            ...     topic="My Topic",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.setTopic", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def channels_unarchive(self, channel):
        """Unarchives a channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | user         | ``channels:write``  |
        +--------------+---------------------+

        Args:
            channel (str) : Channel to unarchive(default= ``"C1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.channels_unarchive(
            ...     channel="C1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="channels.unarchive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_archive(self, channel):
        """Archives a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to archive(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_archive(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.archive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_create(self, name, team_id="T1234567890", validate=True):
        """Creates a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            name (str)      : Name of private channel to create
            team_id (str)   : encoded team id to create the channel in, required if org token is used(default= ``"T1234567890"`` )
            validate (bool) : Whether to return errors on invalid channel name instead of modifying it to meet the specified criteria.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_create(
            ...     name=None,
            ...     team_id="T1234567890",
            ...     validate=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.create", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_createChild(self, channel):
        """Clones and archives a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to clone and archive.(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_createChild(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.createChild", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def groups_history(self, channel, count=100, inclusive=True, latest=1234567890.123456, oldest=1234567890.123456, unreads=True):
        """Fetches history of messages and events from a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:history``  |
        +--------------+---------------------+
        | user         | ``groups:history``  |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)    : Private channel to fetch history for.(default= ``"G1234567890"`` )
            count (int)      : Number of messages to return, between 1 and 1000.(default= ``100`` )
            inclusive (bool) : Include messages with latest or oldest timestamp in results.(default= ``True`` )
            latest (float)   : End of time range of messages to include in results.(default= ``1234567890.123456`` )
            oldest (float)   : Start of time range of messages to include in results.(default= ``1234567890.123456`` )
            unreads (bool)   : Include  ``unread_count_display``  in the output?(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_history(
            ...     channel="G1234567890",
            ...     count=100,
            ...     inclusive=True,
            ...     latest=1234567890.123456,
            ...     oldest=1234567890.123456,
            ...     unreads=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.history", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def groups_info(self, channel, include_locale=True):
        """Gets information about a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:read``     |
        +--------------+---------------------+
        | user         | ``groups:read``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)         : Private channel to get info on(default= ``"G1234567890"`` )
            include_locale (bool) : Set this to  ``True``  to receive the locale for this group. Defaults to  ``False`` (default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_info(
            ...     channel="G1234567890",
            ...     include_locale=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.info", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def groups_invite(self, channel, user):
        """Invites a user to a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to invite user to.(default= ``"G1234567890"`` )
            user (str)    : User to invite.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_invite(
            ...     channel="G1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.invite", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_kick(self, channel, user):
        """Removes a user from a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to remove user from.(default= ``"G1234567890"`` )
            user (str)    : User to remove from private channel.(default= ``"W1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_kick(
            ...     channel="G1234567890",
            ...     user="W1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.kick", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_leave(self, channel):
        """Leaves a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to leave(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_leave(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.leave", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", exclude_archived=True, exclude_members=True, limit=20, team_id="T1234567890"):
        """Lists private channels that the calling user has access to.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:read``     |
        +--------------+---------------------+
        | user         | ``groups:read``     |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            cursor (str)            : Parameter for pagination. Set  ``cursor``  equal to the  ``next_cursor``  attribute returned by the previous request's  ``response_metadata`` . This parameter is optional, but pagination is mandatory: the default value simply fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more details.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            exclude_archived (bool) : Don't return archived private channels.(default= ``True`` )
            exclude_members (bool)  : Exclude the  ``members``  from each  ``group`` (default= ``True`` )
            limit (int)             : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached.(default= ``20`` )
            team_id (str)           : encoded team id to list channels in, required if org token is used(default= ``"T1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     exclude_archived=True,
            ...     exclude_members=True,
            ...     limit=20,
            ...     team_id="T1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def groups_mark(self, channel, ts):
        """Sets the read cursor in a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Channel or conversation to set the read cursor for.(default= ``"C012345678"`` )
            ts (float)    : Unique identifier of message you want marked as most recently seen in this conversation.(default= ``1593473566.0002`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_mark(
            ...     channel="C012345678",
            ...     ts=1593473566.0002,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.mark", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_open(self, channel):
        """Opens a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to open.(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_open(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.open", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_rename(self, channel, name, validate=True):
        """Renames a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str)   : Private channel to rename(default= ``"G1234567890"`` )
            name (str)      : New name for private channel.
            validate (bool) : Whether to return errors on invalid channel name instead of modifying it to meet the specified criteria.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_rename(
            ...     channel="G1234567890",
            ...     name=None,
            ...     validate=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.rename", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_replies(self, channel, thread_ts):
        """Retrieve a thread of messages posted to a private channel
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:history``  |
        +--------------+---------------------+
        | user         | ``groups:history``  |
        +--------------+---------------------+

        Args:
            channel (str)     : Private channel to fetch thread from(default= ``"C1234567890"`` )
            thread_ts (float) : Unique identifier of a thread's parent message(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_replies(
            ...     channel="C1234567890",
            ...     thread_ts=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.replies", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def groups_setPurpose(self, channel, purpose):
        """Sets the purpose for a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to set the purpose of(default= ``"G1234567890"`` )
            purpose (str) : The new purpose(default= ``"My Purpose"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_setPurpose(
            ...     channel="G1234567890",
            ...     purpose="My Purpose",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.setPurpose", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_setTopic(self, channel, topic):
        """Sets the topic for a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to set the topic of(default= ``"G1234567890"`` )
            topic (str)   : The new topic(default= ``"My Topic"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_setTopic(
            ...     channel="G1234567890",
            ...     topic="My Topic",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.setTopic", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def groups_unarchive(self, channel):
        """Unarchives a private channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``groups:write``    |
        +--------------+---------------------+
        | user         | ``groups:write``    |
        +--------------+---------------------+

        Args:
            channel (str) : Private channel to unarchive(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.groups_unarchive(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="groups.unarchive", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def im_close(self, channel):
        """Close a direct message channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``im:write``        |
        +--------------+---------------------+
        | user         | ``im:write``        |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Direct message channel to close.(default= ``"D1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.im_close(
            ...     channel="D1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="im.close", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def im_history(self, channel, count=100, inclusive=True, latest=1234567890.123456, oldest=1234567890.123456, unreads=True):
        """Fetches history of messages and events from direct message channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``im:history``      |
        +--------------+---------------------+
        | user         | ``im:history``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)    : Direct message channel to fetch history for.(default= ``"D1234567890"`` )
            count (int)      : Number of messages to return, between 1 and 1000.(default= ``100`` )
            inclusive (bool) : Include messages with latest or oldest timestamp in results.(default= ``True`` )
            latest (float)   : End of time range of messages to include in results.(default= ``1234567890.123456`` )
            oldest (float)   : Start of time range of messages to include in results.(default= ``1234567890.123456`` )
            unreads (bool)   : Include  ``unread_count_display``  in the output?(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.im_history(
            ...     channel="D1234567890",
            ...     count=100,
            ...     inclusive=True,
            ...     latest=1234567890.123456,
            ...     oldest=1234567890.123456,
            ...     unreads=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="im.history", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def im_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20):
        """Lists direct message channels for the calling user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``im:read``         |
        +--------------+---------------------+
        | user         | ``im:read``         |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            cursor (str) : Paginate through collections of data by setting the  ``cursor``  parameter to a  ``next_cursor``  attribute returned by a previous request's  ``response_metadata`` . Default value fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more detail.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)  : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the users list hasn't been reached.(default= ``20`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.im_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="im.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def im_mark(self, channel, ts):
        """Sets the read cursor in a direct message channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``im:write``        |
        +--------------+---------------------+
        | user         | ``im:write``        |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Direct message channel to set reading cursor in.(default= ``"D1234567890"`` )
            ts (float)    : Timestamp of the most recently seen message.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.im_mark(
            ...     channel="D1234567890",
            ...     ts=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="im.mark", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def im_open(self, user, include_locale=True, return_im=True):
        """Opens a direct message channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``im:write``        |
        +--------------+---------------------+
        | user         | ``im:write``        |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            user (str)            : User to open a direct message channel with.(default= ``"W1234567890"`` )
            include_locale (bool) : Set this to  ``True``  to receive the locale for this im. Defaults to  ``False`` (default= ``True`` )
            return_im (bool)      : Boolean, indicates you want the full IM channel definition in the response.(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.im_open(
            ...     user="W1234567890",
            ...     include_locale=True,
            ...     return_im=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="im.open", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def im_replies(self, channel, thread_ts):
        """Retrieve a thread of messages posted to a direct message conversation
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``im:history``      |
        +--------------+---------------------+
        | user         | ``im:history``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)     : Direct message channel to fetch thread from(default= ``"C1234567890"`` )
            thread_ts (float) : Unique identifier of a thread's parent message(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.im_replies(
            ...     channel="C1234567890",
            ...     thread_ts=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="im.replies", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def mpim_close(self, channel):
        """Closes a multiparty direct message channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``mpim:write``      |
        +--------------+---------------------+
        | user         | ``mpim:write``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : MPIM to close.(default= ``"G1234567890"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.mpim_close(
            ...     channel="G1234567890",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="mpim.close", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def mpim_history(self, channel, count=100, inclusive=True, latest=1234567890.123456, oldest=1234567890.123456, unreads=True):
        """Fetches history of messages and events from a multiparty direct message.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``mpim:history``    |
        +--------------+---------------------+
        | user         | ``mpim:history``    |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str)    : Multiparty direct message to fetch history for.(default= ``"G1234567890"`` )
            count (int)      : Number of messages to return, between 1 and 1000.(default= ``100`` )
            inclusive (bool) : Include messages with latest or oldest timestamp in results.(default= ``True`` )
            latest (float)   : End of time range of messages to include in results.(default= ``1234567890.123456`` )
            oldest (float)   : Start of time range of messages to include in results.(default= ``1234567890.123456`` )
            unreads (bool)   : Include  ``unread_count_display``  in the output?(default= ``True`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.mpim_history(
            ...     channel="G1234567890",
            ...     count=100,
            ...     inclusive=True,
            ...     latest=1234567890.123456,
            ...     oldest=1234567890.123456,
            ...     unreads=True,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="mpim.history", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def mpim_list(self, cursor="dXNlcjpVMDYxTkZUVDI=", limit=20):
        """Lists multiparty direct message channels for the calling user.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``mpim:read``       |
        +--------------+---------------------+
        | user         | ``mpim:read``       |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            cursor (str) : Parameter for pagination. Set  ``cursor``  equal to the  ``next_cursor``  attribute returned by the previous request's  ``response_metadata`` . This parameter is optional, but pagination is mandatory: the default value simply fetches the first "page" of the collection. See `pagination <https://api.slack.com/docs/pagination>`_ for more details.(default= ``"dXNlcjpVMDYxTkZUVDI="`` )
            limit (int)  : The maximum number of items to return. Fewer than the requested number of items may be returned, even if the end of the list hasn't been reached.(default= ``20`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.mpim_list(
            ...     cursor="dXNlcjpVMDYxTkZUVDI=",
            ...     limit=20,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="mpim.list", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

    def mpim_mark(self, channel, ts):
        """Sets the read cursor in a multiparty direct message channel.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``mpim:write``      |
        +--------------+---------------------+
        | user         | ``mpim:write``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            channel (str) : Channel or conversation to set the read cursor for.(default= ``"C012345678"`` )
            ts (float)    : Unique identifier of message you want marked as most recently seen in this conversation.(default= ``1593473566.0002`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.mpim_mark(
            ...     channel="C012345678",
            ...     ts=1593473566.0002,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="mpim.mark", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def mpim_open(self, users):
        """This method opens a multiparty direct message.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``mpim:write``      |
        +--------------+---------------------+
        | user         | ``mpim:write``      |
        +--------------+---------------------+
        | classic bot  | ``bot``             |
        +--------------+---------------------+

        Args:
            users (str) : Comma separated lists of users.  The ordering of the users is preserved whenever a MPIM group is returned.(default= ``"W1234567890,U2345678901,U3456789012"`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.mpim_open(
            ...     users="W1234567890,U2345678901,U3456789012",
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="mpim.open", 
            http_method="POST", 
            content_types=['application/x-www-form-urlencoded', 'application/json'],
            **params,        
        )

    def mpim_replies(self, channel, thread_ts):
        """Retrieve a thread of messages posted to a direct message conversation from a multiparty direct message.
        
        +--------------+---------------------+
        | Token type   | Required scope(s)   |
        +==============+=====================+
        | bot          | ``mpim:history``    |
        +--------------+---------------------+
        | user         | ``mpim:history``    |
        +--------------+---------------------+

        Args:
            channel (str)     : Multiparty direct message channel to fetch thread from.(default= ``"C1234567890"`` )
            thread_ts (float) : Unique identifier of a thread's parent message.(default= ``1234567890.123456`` )
        
        Examples:
            >>> import os
            >>> from pycharmers.sdk import SlackClient
            >>> client = SlackClient(token=os.environ["SLACK_BOT_TOKEN"])
            >>> res = client.mpim_replies(
            ...     channel="C1234567890",
            ...     thread_ts=1234567890.123456,
            >>> )
            
        """
        params = locals()
        params.pop("self")
        self._api_wrapper(
            api_method="mpim.replies", 
            http_method="GET", 
            content_types=['application/x-www-form-urlencoded'],
            **params,        
        )

