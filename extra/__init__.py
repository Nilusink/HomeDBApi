"""
__init__.py
09. January 2023

<description>

Author:
Nilusink
"""
from contextlib import contextmanager
from traceback import format_exc


class ConsoleColors:
    """
    for better readability (colors) in the console
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@contextmanager
def catch_error(*_args, **_kwargs):
    """
    catches errors and prints them, then raises them again
    """
    try:
        yield

    except (Exception,) as e:
        print(
            ConsoleColors.FAIL
            + f"\n\n{' ERROR ':#^64}\n"
            + format_exc()
            + f"\n{' ERROR End ':#^64}\n\n"
            + ConsoleColors.ENDC
        )
        raise e
