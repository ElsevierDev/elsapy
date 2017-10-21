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

def get_logger(name):
    # create logger with module name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create log path, if not already there
    logPath = Path('logs')
    if not logPath.exists():
        logPath.mkdir()
    # create file handler which logs even debug messages
    fh = logging.FileHandler('logs/elsapy-%s.log' % time.strftime('%Y%m%d'))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("Module loaded.")
    return logger