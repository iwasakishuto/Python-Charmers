"""Generate all test codes from Examples in docstring."""
# coding: utf-8
import os
import re
from pathlib import Path
from pycharmers.utils._path import MODULE_DIR, _makedirs
from pycharmers.utils.inspect_utils import get_defined_members, get_imported_members
from pycharmers.utils._colorings import toGREEN, toBLUE

tab = " "*4
remove_sections = ["Note:", "Reference"]
TEST_DIR = MODULE_DIR.replace("pycharmers", "tests")
REMOVE_FUNCIONS = ["def_html"]

p = Path(MODULE_DIR)
for init in p.glob("**/__init__.py"):
    init = str(init)
    subpackage_name = init.split("/")[-2]
    if subpackage_name == "pycharmers": 
        continue
    test_subpackage_dir = os.path.join(TEST_DIR, subpackage_name)
    _makedirs(name=test_subpackage_dir, verbose=False)
    print(f"* {toGREEN(subpackage_name)}")
    exec(f"from pycharmers.{subpackage_name} import *")
    for submodule_name in get_imported_members(init).keys():
        submodule_match = re.match(pattern=r"\.((?!_).+)", string=submodule_name)
        if submodule_match is None: 
            continue
        lines = ["# coding: utf-8\n"]
        file_name = submodule_match.group(1)
        test_filename = f"test_{file_name}.py"
        for funcclass, member in get_defined_members(eval(file_name)).items():
            if (member.__doc__ is None) or ("Examples:\n" not in member.__doc__) or (funcclass in REMOVE_FUNCIONS):
                continue
            line = f"def test_{funcclass}():\n"
            example = member.__doc__[member.__doc__.index("Examples:\n")+10:]
            # Delete unnecessary lines          
            for section in remove_sections: example = example[:example.find(section)]    
            indent = example.index(">")
            for exa_line in example.split("\n"):
                if len(exa_line) < indent:
                    line += "\n"                        
                elif exa_line[indent] in [">", "."]:
                    line += tab + exa_line[indent+4:] + "\n"
                else:
                    line += tab + "# " + exa_line[indent:] + "\n"
            lines.append(line)
        if len(lines)>0:
            print(f"\t* {toBLUE(test_filename)}")
            with open(os.path.join(test_subpackage_dir, test_filename), mode="w") as f_test:
                f_test.writelines(lines)