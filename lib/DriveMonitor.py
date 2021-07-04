import os
import logging
from datetime import datetime
from time import sleep
from threading import Thread

class DriveMonitor(Thread):
    '''
    class responsible for monitoring whether request files are present
    in google drive
    '''
    def __init__(self, service, args):
        Thread.__init__(self)        
        self.args = args
        self.logger = logging.getLogger("catmonitor.DriveMonitor")
        self.keep_running = True        
        self.counter = 0        
        self.service = service        
        self.requests_dir = self.service.get_requests_dir()

    def _parse(self):
        queue = []
        files = [file for file in os.listdir(self.requests_dir) if not file.endswith("_parsed")]
        while len(files) is not 0:
            file = files.pop(0)
            self.logger.info("found request file {0}".format(file))
            filepath = os.path.join(self.requests_dir, file)

            with open(filepath, 'rb') as f:
                vidindex = list(map(int, f.read().split(',')))

            outpath = os.path.abspath(self.args.output)
            vids = [f for f in os.listdir(outpath) if os.path.isfile(os.path.join(outpath, f))]
            vids = [f for f in vids if f.endswith(".mp4")]
            vids.sort(key=lambda x: -os.path.getmtime(outpath + "/" + x))

            for i in vidindex:
                if 0 <= i - 1 < len(vids):
                    if vids[i - 1] not in queue:
                        item = os.path.abspath(os.path.join(self.args.output, vids[i - 1])                )
                        queue.append(item)

            self.logger.debug("{0} parsed, renaming".format(file))
            os.rename(filepath, filepath + "_parsed")
            self.service.upload(queue, self.service.get_root_dir(), "video/mp4")
                    
    def run(self):
        # round interval to make sure the elif condition is triggered for uneven intervals
        rounded_interval = self.args.polling_interval if self.args.polling_interval % 2 == 0 else self.args.polling_interval + 1        
        while self.keep_running:            
            if self.counter > self.args.polling_interval:
                # check if there is a list file   
                self.service.check_list_files_request()
                self.service.check_video_request()
                self.counter = 0            
            elif self.counter * 2 == rounded_interval:
                self.service.check_list_files_request()
                self.counter += 1
                pass
            else:                
                self.counter += 1
                self._parse()                
                    
            sleep(1)            
            
    def stop(self):
        self.keep_running = False
