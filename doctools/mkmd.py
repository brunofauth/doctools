from __future__ import annotations

from typing import AnyStr
from collections.abc import Sequence, Iterable

import fire
import glob
import os
import pathlib
import re
import sys
import subprocess as sp

from .path import CONTENTS_DIR, HISTORY_FILE
from .common import normalize_file_name, register_readline
from fzf_but_typed.lib import fzf_iter

RE_MD_FILE = re.compile(r'^(\d{2})_[-\w]+\.md$')


def _available_categories() -> Iterable[AnyStr]:
    entry: os.DirEntry
    for entry in os.scandir(CONTENTS_DIR):
        if entry.is_dir() and not entry.name.startswith("."):
            yield entry.name


def cli(*raw_titles: str, category: str | None = None):
    categories = list(_available_categories())
    if category is None:
        category = fzf_iter(categories)[0]
    if category not in categories:
        raise ValueError(f"Invalid category: {category}\nAvailable categories: {categories}")

    siblings_all = (e.name for e in os.scandir(CONTENTS_DIR / category) if e.is_file())
    siblings_md = (
        match for fname in siblings_all if (match := RE_MD_FILE.match(fname)) is not None)
    siblings_prefix_num = (int(match.group(1)) for match in siblings_md)
    index = max(siblings_prefix_num, default=0) + 1

    names: Sequence[str]
    if len(raw_titles) != 0:
        names = raw_titles
    else:
        get_name = lambda: input("Enter filename (leave it empty to exit): ").strip()
        names = [name for name in iter(get_name, "")]
        if len(names) == 0:
            print("No names given. Exiting...", file=sys.stderr)
            raise SystemExit

    make_filename = lambda name: pathlib.Path(normalize_file_name(name)).with_suffix(".md")
    file_names = [make_filename(name) for name in names]
    make_filepath = lambda offset, name: CONTENTS_DIR / category / f"{index+offset:0=2d}_{name}"
    file_pathes = [make_filepath(i, file) for i, file in enumerate(file_names)]
    titles = [(name.title() if name.isupper() or name.islower() else name) for name in names]

    for path, title in zip(file_pathes, titles):
        path.write_text("---\n"
                        f"title: {title}\n"
                        "...\n"
                        "\n"
                        "# Introdução\n"
                        "\n")

    HISTORY_FILE.write_text(str(file_pathes[-1]))
    editor = os.environ.get("EDITOR", "vim")
    os.execvp(editor, [
        editor,
        "--",
        str(file_pathes[-1]),
        *glob.glob("**/*.md", recursive=True),
    ])


def main() -> None:
    register_readline()
    try:
        fire.Fire(cli)
    except sp.CalledProcessError as e:
        if e.returncode == 130 and e.args[0] == 'fzf':
            return
        raise
