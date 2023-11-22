from __future__ import annotations

import pathlib
import os
import fire
import shlex
import subprocess as sp

from .common import normalize_file_name, register_readline
from .path import CONTENTS_DIR
from typing import Iterable
from fzf_but_typed.lib import (
    FuzzyFinderBuilder,
    ScriptingOptions,
    InterfaceOptions,
    Binding,
    Key,
    ActionSimple,
)

# yapf: disable
YAML_HEADER_TEMPLATE = (
    "---\n"
    "title: {title}\n"
    "...\n"
    "\n"
)

MD_INCLUDE_TEMPLATE = (
    "# {file_title}\n"
    "!INCLUDE '{file_path}', 1\n"
    "\n"
)
# yapf: enable


def read_header_lines(file_path: pathlib.Path) -> Iterable[str]:
    with open(file_path) as file:
        lines = iter(file)
        if next(lines, "") != "---\n":
            return
        while (line := next(lines, None)) not in ("...\n", None):
            yield line   # type: ignore


def get_title(header_lines: Iterable[str]) -> str | None:
    for line in header_lines:
        if line.startswith("title:"):
            return line[len("title: "):].strip()
    return None   # Redundant line for mypy's sake...


def discover_md_files() -> str:
    return sp.run(
        shlex.split("find . -type f -name *.md -print0"),
        cwd=CONTENTS_DIR,
        text=True,
        check=True,
        stdout=sp.PIPE,
    ).stdout


def cli(
    *files: str,
    title: str | None = None,
    output_file: str | None = None,
    edit: bool = False,
) -> None:
    if title is None:
        title = input("Title for mdpp file (not filename): ")
    if output_file is None:
        output_file = normalize_file_name(title)
        print("No output file specified, using: '{output_file!s}.mdpp'")

    if len(files) == 0:
        files = FuzzyFinderBuilder(
            scripting=ScriptingOptions(read0=True),
            interface=InterfaceOptions(bind=[
                Binding(binding=Key.CTRL_A, action=ActionSimple.SELECT_ALL),
                Binding(binding=Key.ENTER, action=ActionSimple.ACCEPT_NON_EMPTY),
                Binding(binding=Key.ESC, action=ActionSimple.CANCEL),
            ])).build().run(discover_md_files(), check=True).output

    file_paths = [pathlib.Path(file).absolute() for file in files if file.endswith(".md")]
    output_path = pathlib.Path(output_file).absolute().with_suffix(".mdpp")
    output_dir = output_path.parent

    with open(output_path, "w") as dst:
        dst.write(YAML_HEADER_TEMPLATE.format(title=title))
        dst.writelines(
            MD_INCLUDE_TEMPLATE.format(
                file_title=get_title(read_header_lines(fp)) or "",
                file_path=fp.relative_to(output_dir),
            ) for fp in file_paths)

    if edit:
        os.execvp(os.environ.get("EDITOR", "vim"), ["--", str(output_path)])


def main() -> None:
    register_readline()
    fire.Fire(cli)
