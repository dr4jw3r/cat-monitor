import os
import logging
import subprocess

from time import sleep
from threading import Thread

class Converter(Thread):
    '''
    class responsible for converting the .h264 videos to .mp4
    '''
    def __init__(self, args):
        Thread.__init__(self)
        self.keeprunning = True
        self.queue = []
        self.logger = logging.getLogger("catmonitor.Converter")
        
    '''
    --- private functions ---
    '''
    def _convert(self, filename):
        command = "MP4Box -add {0}.h264 {1}.mp4".format(filename, filename)    
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)            
            os.remove(filename + ".h264")
            self.logger.debug("converted " + filename)
            return 0
        except subprocess.CalledProcessError as e:
            self.logger.error('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
            return 1
        
    '''
    --- public functions ---
    '''
    def run(self):
        while self.keeprunning or len(self.queue) is not 0:            
            if len(self.queue) is not 0:
                filename = self.queue.pop(0)
                self._convert(filename)
                
            sleep(1)
    
    def stop(self):
        self.keeprunning = False        

    def enqueue(self, filename):
        self.logger.debug("adding {0} to conversion queue".format(filename))
        self.queue.append(filename)        