import glob
import os

from time import sleep
from threading import Thread

from Logger import Logger

class FileMonitor(Thread):
    """
    Class for monitoring the created recordings
    """
    def __init__(self, args):
        Thread.__init__(self)
        self.args = args
        self.outputdir = args.output
        self.logger = Logger(args, type(self).__name__)
                
        if not os.path.exists(self.outputdir):
            self.logger.verbose("directory {0} not found, creating".format(self.outputdir))
            os.mkdir(self.outputdir)
        
        self.keeprunning = True
        
    def run(self):
        while self.keeprunning:
            files = [f for f in os.listdir(self.outputdir) if os.path.isfile(os.path.join(self.outputdir, f))]
            files = [f for f in files if f.endswith(".mp4")]
            
            if len(files) > self.args.number:                
                files.sort(key=lambda x: os.path.getmtime(self.outputdir + "/" + x))
                oldest = files.pop(0)
                os.remove(self.args.output + "/" + oldest)
                self.logger.verbose("removed " + oldest)
            
            sleep(1)
    
    def stop(self):        
        self.keeprunning = False