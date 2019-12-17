import logging
import os.path

from datetime import datetime
from lib.ArgumentParser import createparser
from lib.Monitor import Monitor


def setup_logging(args):
    '''
    this function sets up the logging for the entire application
    '''
    logs_path = os.path.abspath('./logs')
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    logger = logging.getLogger('catmonitor')
    logger.setLevel(logging.DEBUG)
    log_file = os.path.join(logs_path), datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".log")

    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()

    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s]\t%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    args = createparser()
    setup_logging(args)

    monitor = Monitor(args)
    exit(monitor.start())
