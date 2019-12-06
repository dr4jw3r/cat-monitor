from datetime import datetime
from time import sleep
from threading import Thread
from picamera import PiCamera, Color

class Camera(object):
    def __init__(self, args):
        self.picam = None
        self.create(args)
        self.timethread = TimeUpdateThread(self.picam)
    
    def create(self, args):
        self.picam = PiCamera()
        self.picam.rotation = args.rotation
        self.picam.framerate = args.fps
        self.picam.resolution = (args.width, args.height)            
        self.picam.annotate_text_size = 50
    
    def start_preview(self):
        self.picam.start_preview()
        self.timethread.start()
        
    def stop_preview(self):
        self.picam.stop_preview()
        self.timethread.stop()


class TimeUpdateThread(Thread):
    def __init__(self, camera):
        Thread.__init__(self)
        self.camera = camera
        self.keeprunning = True        
    
    def run(self):
        while self.keeprunning:
            time = datetime.now().strftime("%d %b %Y, %H:%M:%S")
            self.camera.annotate_text = time
            sleep(0.5)
            
    def stop(self):
        self.keeprunning = False
        
    