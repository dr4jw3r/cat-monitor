import logging
import os.path
from datetime import datetime
from lib.ArgumentParser import createparser
from lib.Monitor import Monitor

def setup_logging(args):
    if not os.path.exists(os.path.abspath('./logs')):
        os.mkdir(os.path.abspath('./logs'))

    logger = logging.getLogger('catmonitor')
    logger.setLevel(logging.DEBUG)
    logfile = os.path.join(os.path.abspath('./logs'), datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".log")

    fh = logging.FileHandler(logfile)
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
