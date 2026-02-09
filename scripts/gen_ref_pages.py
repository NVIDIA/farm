# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate the code reference pages and navigation."""

from pathlib import Path
import importlib.util
from griffe.dataclasses import Docstring
from itertools import chain
import mkdocs_gen_files

import yaml

nav = mkdocs_gen_files.Nav()

root = Path(__file__).parent.parent

# load configuration file
config_path = Path(__file__).parent / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

for package_obj in config["docs"]:
    for package, _ in package_obj.items():
        src = root / Path(package.replace(".", "/"))
        for path in sorted(chain(src.rglob("*.py"), src.rglob("*.toml"))):
            module_path = package / path.relative_to(src).with_suffix("")
            doc_path = path.relative_to(src).with_suffix(".md")
            full_doc_path = Path("reference", doc_path)
            parts = tuple(module_path.parts)

            if parts[-1] == "__init__":
                parts = parts[:-1]
            elif parts[-1] == "__main__":
                continue
            if not parts:
                continue
            nav[parts] = doc_path.as_posix()

            with mkdocs_gen_files.open(full_doc_path, "w") as fd:
                if ".toml" not in str(path):
                    identifier = ".".join(parts)
                    print("::: " + identifier, file=fd)
                else:
                    print("```Toml", file=fd)
                    print("{! " + str(path) + " !}", file=fd)
                    print("```", file=fd)

            mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

# Add configuration file to docs
nav = mkdocs_gen_files.Nav()


for package_obj in config["docs"]:
    for package, config_funcs in package_obj.items():
        src = root / Path(package.replace(".", "/"))
        config_md = ""
        for config_func_name in config_funcs["config_funcs"]:
            path = src / Path(config_func_name.replace(".", "/")).with_suffix(".py")
            doc_path = Path("settings.md")
            full_doc_path = Path("settings", doc_path)
            parts = tuple(doc_path.with_suffix("").parts)
            actual_config_fn_name = config_func_name.split(".")[-1]
            config_mod = ".".join([package] + config_func_name.split(".")[:-1])
            nav[parts] = doc_path.as_posix()
            config_func = getattr(importlib.import_module(config_mod), actual_config_fn_name)

            # replace settings_package_name with the package name, reqd because of coming from sphinx
            patched_docstring = config_func.__doc__.replace("settings_package_name", package)
            config_docstring = Docstring(patched_docstring, lineno=1)
            parsed_docstring = config_docstring.parse("google")[0]
            config_md += f"\n\n## {actual_config_fn_name}\n\n"
            config_md += parsed_docstring.value

            with mkdocs_gen_files.open(full_doc_path, "w") as fd:
                print(config_md, file=fd)
            mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

# the case where there are no configuration settings
if not nav._data:
    nav[Path("settings").parts] = Path("settings.md").as_posix()
    with mkdocs_gen_files.open(Path("settings", "settings.md"), "w") as fd:
        print('!!! info "No defined settings available"', file=fd)

with mkdocs_gen_files.open("settings/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
