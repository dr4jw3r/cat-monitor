import os
import subprocess

from time import sleep
from threading import Thread

class Converter(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.keeprunning = True
        self.queue = []
        
    def _convert(self, filename):
        command = "MP4Box -add {0}.h264 {1}.mp4".format(filename, filename)    
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)            
            os.remove(filename + ".h264")
            return 0
        except subprocess.CalledProcessError as e:
            print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
            return 1
        
    def run(self):
        while self.keeprunning and len(self.queue) is 0:
            sleep(1)            
            
            if len(self.queue) is not 0:
                filename = self.queue.pop(0)
                self._convert(filename)                
    
    def stop(self):
        self.keeprunning = False

    def enqueue(self, filename):        
        self.queue.append(filename)        