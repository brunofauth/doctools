from __future__ import annotations

import os
import pathlib

try:
    REPO_ROOT_DIR = pathlib.Path(os.environ["DOCTOOLS_MD_REPO_ROOT"]).absolute()
except KeyError as error:
    print(f"env variable {error.args[0]!r} not set. Exiting...")
    raise SystemExit

try:
    CONTENTS_DIR = pathlib.Path(os.environ["DOCTOOLS_CONTENTS_DIR"])
except KeyError:
    CONTENTS_DIR = REPO_ROOT_DIR / "contents"

try:
    HISTORY_FILE = pathlib.Path(os.environ["DOCTOOLS_HISTORY_FILE"])
except KeyError:
    HISTORY_FILE = REPO_ROOT_DIR / ".editmd-last-file"

PACKAGE_ROOT_DIR = pathlib.Path(__file__).parent.absolute()
PANDOC_TEX_HEADER_FILE = PACKAGE_ROOT_DIR / "header.tex"
PANDOC_YML_METADATA_FILE = PACKAGE_ROOT_DIR / "metadata.yml"
