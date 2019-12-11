import logging
from datetime import datetime
from time import sleep
from threading import Thread
from picamera import PiCamera, Color

class Camera(object):
    def __init__(self, args):
        self.logger = logging.getLogger("catmonitor.Camera")
        self.picam = None
        self.create(args)
        self.timethread = TimeUpdateThread(self.picam)                
    
    def stoptimer(self):
        self.timethread.stop()
        self.timethread.join()
    
    def create(self, args):
        self.picam = PiCamera()
        self.picam.rotation = args.rotation
        self.picam.framerate = args.fps
        self.picam.resolution = (args.width, args.height)            
        self.picam.annotate_text_size = 50        
        self.logger.debug("camera created")
    
    def start_preview(self):
        self.picam.start_preview(fullscreen=False, window=(100, 100, 800, 600))
        
        if not self.timethread.isAlive():
            self.timethread.start()
        
    def stop_preview(self):
        self.picam.stop_preview()
        self.stoptimer()
        
    def start_recording(self, filename):
        self.picam.start_recording(filename)
        
        if not self.timethread.isAlive():
            self.timethread.start()
        
    def stop_recording(self):
        self.picam.stop_recording()
        self.stoptimer()
        
    def split_recording(self, filename):
        self.picam.split_recording(filename + ".h264")
        
    def wait_recording(self, time):
        self.picam.wait_recording(time)

class TimeUpdateThread(Thread):
    def __init__(self, camera):
        Thread.__init__(self)
        self.camera = camera
        self.keeprunning = True        
    
    def run(self):
        while self.keeprunning:
            time = datetime.now().strftime("%d %b %Y, %H:%M:%S")
            self.camera.annotate_text = time
            sleep(1)
            
    def stop(self):
        self.keeprunning = False
        
    