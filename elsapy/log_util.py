"""A logging module for use with elsapy.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

import time, logging
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

## Following adapted from https://docs.python.org/3/howto/logging-cookbook.html


# A collection of singletons. Allows to e.g. manipulate file handles at runtime
LOGGERS = {}


def _make_logger(name):
    """
    .. note::

      Do not call this function! To get a logger, use get_logger instead.
    """
    # create logger with module name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create console handler with error log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handler to the logger
    logger.addHandler(ch)
    logger.info(f"Logger created: {name}")
    return logger


def get_logger(name):
    """
    Returns a logger with the given name. If it doesn't exist, creates,
    stores and returns the new logger.
    """
    if name not in LOGGERS:
        LOGGERS[name] = _make_logger(name)
    return LOGGERS[name]


def add_file_handle_to_logger(lgr, output_dir):
    """
    :returns: None. This function adds a ``FileHandler`` to the given logger,
      to write a log file inside the given ``output_dir``.
    """
    # create log path, if not already there
    logPath = Path(output_dir)
    if not logPath.exists():
        logPath.mkdir()
    # create file handler with debug log level
    fh = logging.FileHandler(logPath / f'elsapy-{time.strftime("%Y%m%d")}.log')
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handler to the logger
    lgr.addHandler(fh)

