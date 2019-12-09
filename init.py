from time import sleep
from lib.ArgumentParser import createparser
from lib.Monitor import Monitor
from lib.Logger import Logger

if __name__ == "__main__":
    args = createparser()
    
    logger = Logger(args, "init")
    monitor = Monitor(args)
    
    logger.log("[ MONITOR RUNNING ]")
    exit(monitor.start())