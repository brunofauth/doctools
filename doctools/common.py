from __future__ import annotations

import unicodedata


def _remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode("utf-8")
    return only_ascii


def normalize_file_name(file_name: str) -> str:
    table = str.maketrans(
        " \t",  # From these
        "-_",  # to these
        "()[]{}\"'")  # And delete these
    return _remove_accents(file_name.translate(table)).lower()


def register_readline():
    try:
        import readline
        import rlcompleter
    except ImportError:
        return

    # Reading the initialization (config) file may not be enough to set a
    # completion key, so we set one first and then read the file.
    has_libedit = 'libedit' in getattr(readline, '__doc__', '')
    readline.parse_and_bind(
        'bind ^I rl_complete' if has_libedit else 'tab: complete')

    try:
        readline.read_init_file()
    except OSError:
        # An OSError here could have many causes, but the most likely one
        # is that there's no .inputrc file (or .editrc file in the case of
        # Mac OS X + libedit) in the expected location.  In that case, we
        # want to ignore the exception.
        pass
