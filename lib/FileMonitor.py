import glob
import os
import logging

from time import sleep
from threading import Thread

class FileMonitor(Thread):
    """
    Class for monitoring the created recordings
    """
    def __init__(self, args):
        Thread.__init__(self)
        self.args = args
        self.outputdir = args.output
        self.logger = logging.getLogger("catmonitor.FileMonitor")
	self.keeprunning = True

        if not os.path.exists(self.outputdir):
            self.logger.debug("directory {0} not found, creating".format(self.outputdir))
            os.mkdir(self.outputdir)

    def run(self):
        while self.keeprunning:
            files = [f for f in os.listdir(self.outputdir) if os.path.isfile(os.path.join(self.outputdir, f))]
            files = [f for f in files if f.endswith(".mp4")]

            if len(files) > self.args.number:
                files.sort(key=lambda x: os.path.getmtime(self.outputdir + "/" + x))
                oldest = files.pop(0)
                os.remove(self.args.output + "/" + oldest)
                self.logger.debug("removed {0} (oldest)".format(oldest))

            sleep(1)

    def stop(self):
        self.keeprunning = False
