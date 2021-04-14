"""A Python module for use with api.elsevier.com. Its aim is to make life easier
    for people who are not primarily programmers, but need to interact with
    publication and citation data from Elsevier products in a programmatic
    manner (e.g. academic researchers).
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

version = '0.5.0'


from .log_util import LOGGERS, add_file_handle_to_logger


def log_to_directory(dirpath, logger_names=None):
    """
    :param str dirpath: output directory where loggers will write into.
    :param logger_names: Optional list of strings to identify the affected
      loggers by the name given when created via ``get_logger``. If none
      is given, all loggers will be affected.

    When called, existing loggers will start logging their output to the
    provided directory.
    """
    if logger_names is None:
        logger_names = LOGGERS.keys()
    assert all(ln in LOGGERS for ln in logger_names), \
        f"Unknown loggers! {logger_names}"
    for ln in logger_names:
        add_file_handle_to_logger(LOGGERS[ln], dirpath)
