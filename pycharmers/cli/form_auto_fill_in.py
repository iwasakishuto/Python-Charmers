# coding: utf-8
import os
import re
import sys
import copy
import json
import time
from pathlib import Path
import argparse

from ._clipath import PYCHARMERS_CLI_FORM_AUTO_FILL_IN_DIR
from ..utils.driver_utils import get_driver, try_find_element_click, try_find_element_send_keys
from ..utils._colorings import toBLUE, toGREEN, toACCENT
from ..utils.argparse_utils import KwargsParamProcessor
from ..utils.generic_utils import now_str, str_strip, handleKeyError
from ..utils.json_utils import save_json, dumps_json
from ..utils.print_utils import pretty_3quote, tabulate

def form_auto_fill_in(argv=sys.argv[1:]):
    """Auto fill in your form using your saved information (or answer on the spot).

    Args:
        path (str)                         : Path to environment file.
        -remain-unchanged (bool)           : Whether you want to update and memorize your answer. (default= ``True`` )
        -Y/--yes (bool)                    : Automatic yes to prompts.
        --quiet (bool)                     : Whether you want to be quiet or not. (default= ``False`` )
        --browser (bool)                   : Whether you want to run Chrome with GUI browser. (default= ``True`` )
        -P/--params (KwargsParamProcessor) : Specify the kwargs. You can specify by ``-P username=USERNAME`` ``-P password=PASSWORD``
        --show-data (bool)                 : Print the data in path.

    NOTE:
        When you run from the command line, execute as follows::

            $ form-auto-fill-in UHMRF --yes -P "username=USERNAME" -P "password=PASSWORD"
            $ form-auto-fill-in UHMRF --show-data
            $ form-auto-fill-in

    Examples:
        >>> # Run in terminal
        >>> form-auto-fill-in UHMRF --show-data
        {
            "name": "UTokyo Health Management Report Form",
            "URL": "https://forms.office.com/Pages/ResponsePage.aspx?id=XXXXX",
            "login": {
                "0": {
                "func": "send_keys",
                "by": "xpath",
                :
            }
            :
        }
        >>> form-auto-fill-in
        +--------------+--------------------------------------+
        | Abbreviation |                 Name                 |
        +==============+======================================+
        |        UHMRF | UTokyo Health Management Report Form |
        +--------------+--------------------------------------+
        |      _sample |                         SAMPLE FORMS |
        +--------------+--------------------------------------+
    """
    if len(argv)==0:
        tabulate([[os.path.splitext(fn.name)[0], json.load(fn.open()).get("name", "")] for fn in Path(PYCHARMERS_CLI_FORM_AUTO_FILL_IN_DIR).glob("*.json")], headers=["Abbreviation", "Name"])
        sys.exit(-1)
    parser = argparse.ArgumentParser(prog="form-auto-fill-in", description="Auto fill in your form using your saved information (or answer on the spot).", add_help=True)
    parser.add_argument("path", type=str, help="Path to environment file.")
    parser.add_argument("--remain-unchanged", action="store_true", help="Whether you want to update and memorize your answer. (default=True)")
    parser.add_argument("-Y", "--yes",        action="store_true", help="Automatic yes to prompts.")
    parser.add_argument("--quiet",            action="store_true", help="Whether you want to be quiet or not. (default=False)")
    parser.add_argument("--browser",          action="store_true", help="Whether you want to run Chrome with GUI browser. (default=True)")
    parser.add_argument("-P", "--params", default={}, action=KwargsParamProcessor, help="Specify the kwargs. You can specify by -P username=USERNAME -P password=PASSWORD")
    parser.add_argument("--show-data",  action="store_true", help="Print the data in path.")
    args = parser.parse_args(argv)
    path = args.path
    if not path.endswith(".json"):
        path = os.path.join(PYCHARMERS_CLI_FORM_AUTO_FILL_IN_DIR, path+".json")
    model = AutoFillInForms(path=path)
    if args.show_data:
        model.show_data()
    else:
        model.run(browser=args.browser, update=not args.remain_unchanged, need_check=not args.yes, **args.params)

class AutoFillInForms():
    """If you want to create your own gateway class, please inherit this class.

    Args:
        path (str)     : Path to json data that describes the procedure of form.
        verbose (bool) : Whether to print message or not. (default= ``True`` )

    Attributes:
        print (function) : Print function according to ``verbose``
        data (dict)      : Data that describes the procedure of form.
        path (str)       : Path to json data that describes the procedure of form.
    """
    SUPPORTED_FORM_TYPES = ["radio", "checkbox", "text"]
    DOMAIN2FORM = {
        "forms.office.com": "office",
    }
    def __init__(self, path, verbose=True, **kwargs):
        self.verbose = verbose
        self.print = print if verbose else lambda *args: None
        self.data = self.load_data(path)
        self.path = path
        self.form_type = self.whichForms(self.data["URL"])
        self.__dict__.update(kwargs)
        self.print(*pretty_3quote(f"""
        * Form Name : {toACCENT(self.data.get("name", ""))}
        * Form Type : {toGREEN(self.form_type)}
        * Data Path : {toBLUE(self.path)}
        """))

    @staticmethod
    def load_data(path):
        """Load data from json file.

        Args:
            path (str)    : Path to json file.
        """
        with open(path, mode="r", encoding="utf-8") as fr:
            data = json.load(fr)
        return data

    @staticmethod
    def save_data(path, data, indent=2, update=True):
        """Save data at ``self.path``

        Args:
            path (str)    : Path to json file.
            indent (int)  : If ``indent`` is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines. ``None`` is the most compact representation.
            update (bool) : Whether to update ``"last_date"`` variable.
        """
        if update: 
            data["last_date"] = now_str()
        save_json(obj=data, file=path, indent=2)

    @staticmethod
    def whichForms(url):
        """Decide which Forms from the domain of the ``url``

        Args:
            url (str) : URL of the forms.   

        Returns:
            str : Identifier of the forms. 
        """
        url_domain = re.match(pattern=r"^https?:\/\/(.+?)\/", string=url).group(1)
        handleKeyError(lst=list(AutoFillInForms.DOMAIN2FORM.keys()), url_domain=url_domain)
        return AutoFillInForms.DOMAIN2FORM[url_domain]

    @staticmethod
    def show_curt_browser(driver):
        """Visualize the current browser by taking screenshots

        Args:
            driver (WebDriver) : Selenium WebDriver.
        """
        fn = "tmp.png"
        driver.save_screenshot(fn)
        try:
            from imgcat import imgcat
            imgcat(open(fn))
        except:
            import subprocess
            subprocess.run(["imgcat", fn])
        os.remove(fn)

    @staticmethod
    def answer_question(qno, ans_data={}, inputElements=[], need_check=False):
        """Answer each question.

        Args:
            qno (int)            : Question number in the form.
            inputElements (list) : List of input elements in the form.
            need_check (bool)    : Whether you need to check the value when using the value in environment file. (default= ``False`` )

        Returns:
            dict : ``{"no": no, "val": val}``
        """
        ans = ans_data.get(str(qno))
        input_required = True
        if ans is not None:
            input_required = False
            no = ans.get("no", 1)
            val = ans.get("val", "")
            if need_check:
                print(f"Is your answer correct? [Y/n] :\n{no},{val}")
                input_required = input().lower().startswith("n")
        # Accept input from user.
        if input_required:
            print("Please input Your answer: ", end="")
            no,*val = input().split(",")
        try:
            no = int(no)
        except ValueError:
            val = [no]
            no = 1

        target = inputElements[no-1]
        type = target.get_attribute("type")
        handleKeyError(lst=AutoFillInForms.SUPPORTED_FORM_TYPES, type=type)
        if type == "radio":
            target.click()
        elif type == "checkbox":
            for n in set(val + [no]):
                inputElements[int(n)-1].click()
        elif type == "text":
            if not isinstance(val, str):
                val = str_strip(",".join(val))
            target.send_keys(val)
        return {"no": no, "val": val}

    def show_data(self):
        print(dumps_json(obj=self.data))

    def login(self, driver, url, login_data={}):
        """Perform the login procedure required to answer the form.

        Args:
            driver (WebDriver) : Selenium WebDriver.
            url (str)          : URL of the form.
            login_data (dict)  : Data required for login.
        """
        self.print(f"\nLogin\n{'='*30}\nGet {toBLUE(url)}")
        driver.get(url)
        login_data = copy.deepcopy(sorted(login_data.items(), key=lambda x:x[0]))
        for no,values in login_data:
            {
                "click" : try_find_element_click,
                "send_keys" : try_find_element_send_keys,
            }[values.pop("func")](driver=driver, verbose=self.verbose, **values)

    def run(self, browser=False, **kwargs):
        """
        Args:
            browser (bool) : Whether you want to run Chrome with GUI browser. (default= ``False`` )
        """
        with get_driver(browser=browser) as driver:
            self.login(driver=driver, url=self.data["URL"], login_data=self.data.get("login", {}))
            self.answer_form(driver=driver, **kwargs)

    def dev_run(self, browser=True, **kwargs):
        """
        Args:
            browser (bool) : Whether you want to run Chrome with GUI browser. (default= ``True`` )

        Args:
            WebDriver : Selenium WebDriver.
        """
        driver = get_driver(browser=browser)
        self.login(driver=driver, url=self.data.get("URL"), login_data=self.data.get("login", {}))
        self.answer_form(driver=driver, **kwargs)
        return driver

    def answer_form(self, driver, **kwargs):
        """Answer the forms.

        Args:
            driver (WebDriver) : Selenium WebDriver.       
        """
        if "answer" not in self.data:
            self.data["answer"] = {}
        self.print(f"\nAnswer Form\n{'='*30}")
        getattr(self, f"answer_form_{self.form_type}")(driver=driver, **kwargs)

    def answer_form_office(self, driver, need_check=True, update=True, show_result=True, **kwargs):
        ans_data = self.data["answer"]
        answered_qnos = []
        not_found_count=0
        while True:
            visible_questions = driver.find_elements_by_class_name(name="office-form-question")
            if len(answered_qnos) == 0:
                if not_found_count>5: break
                time.sleep(1)
                not_found_count += 1
            elif len(answered_qnos) == len(visible_questions): 
                break
            for question in visible_questions:
                # NOTE: question number depends on forms.
                qno = int(question.find_element_by_css_selector("span.ordinal-number").text.rstrip("."))
                if qno not in answered_qnos:
                    self.print(question.find_element_by_css_selector("div.question-title-box").text+"\n")
                    inputElements = question.find_elements_by_tag_name(name="input")
                    num_inputElements = len(inputElements)
                    for j,inputTag in enumerate(inputElements):
                        type_ = inputTag.get_attribute("type")
                        value = inputTag.get_attribute("value")
                        # NOTE: input no is 1-based index.
                        self.print(f"\t{j+1:>0{len(str(num_inputElements))}} [{type_}] {value}")
                    answer = self.answer_question(qno=qno, ans_data=ans_data, inputElements=inputElements, need_check=need_check)
                    self.data["answer"][str(qno)] = answer
                    answered_qnos.append(qno)
                    print("-"*30)
        try_find_element_click(driver=driver, by="css selector", identifier="button.__submit-button__")        
        self.save_data(self.path, self.data, update=update)
        if show_result:
            self.print(f"Capturing the current browser...")
            time.sleep(3)
            self.show_curt_browser(driver=driver)