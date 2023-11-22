from __future__ import annotations

import fire
import shlex
import pathlib
import tempfile
import subprocess as sp

from .path import PANDOC_YML_METADATA_FILE, PANDOC_TEX_HEADER_FILE
from fzf_but_typed.lib import FuzzyFinderBuilder, ScriptingOptions


def find_mdpp() -> str:
    return sp.run(
        shlex.split("find -maxdepth 3 -type f -name \*.mdpp -print0"),
        check=True,
        text=True,
        stdout=sp.PIPE,
    ).stdout


def cli(input_mdpp: str | None = None) -> None:
    if input_mdpp is None:
        input_mdpp = FuzzyFinderBuilder(scripting=ScriptingOptions(read0=True)).build().run(
            find_mdpp(), check=True).output[0]
    else:
        assert input_mdpp.endswith('.mdpp'), "Invalid input file"
    mdpp_path = pathlib.Path(input_mdpp).absolute()

    with tempfile.NamedTemporaryFile() as dst_md:
        mdpp_cmd = [
            "mdpp",
            *("--disable", "latex_render"),
            *("--disable", "table_of_contents"),
            *("--disable", "include_url"),
            *("--disable", "include_code"),
            *("--disable", "reference"),
            mdpp_path.name,
        ]
        sp.run(
            mdpp_cmd,
            check=True,
            text=True,
            cwd=mdpp_path.parent,
            stdout=dst_md.fileno(),
        )

        pandoc_cmd = [
            "pandoc",
            *("--include-in-header", str(PANDOC_TEX_HEADER_FILE)),
            *("--metadata-file", str(PANDOC_YML_METADATA_FILE)),
            "--from=markdown+mark",
            "--pdf-engine=lualatex",
            dst_md.name,
            *("--output", str(mdpp_path.with_suffix('.pdf'))),
        ]

        sp.run(
            pandoc_cmd,
            check=True,
            text=True,
        )


def main() -> None:
    try:
        fire.Fire(cli)
    except sp.CalledProcessError as error:
        if error.returncode == 130 and error.args[0] == 'fzf':
            return
        raise
