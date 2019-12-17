import logging
import os.path

from datetime import datetime
from time import sleep
from threading import Thread
from picamera import PiCamera, Color

class Camera(object):
    '''
    class for handling the pi camera functionality
    '''
    def __init__(self, args):
        self.logger = logging.getLogger("catmonitor.Camera")
        self.picam = None
        self._create(args)
        self.timethread = TimeUpdateThread(self.picam)
        self.image_dir = self._get_image_dir()
    
    '''
    --- private functions ---
    '''
    def _create(self, args):
        self.picam = PiCamera()
        self.picam.rotation = args.rotation
        self.picam.framerate = args.fps
        self.picam.resolution = (args.width, args.height)            
        self.picam.annotate_text_size = 25      
        self.logger.debug("camera created")

    def _get_image_dir(self):        
        image_dir = os.path.abspath("./images")
        if not os.path.exists(image_dir):
            self.logger.debug("creating images directory")
            os.mkdir(image_dir)
            
        return image_dir
    
    '''
    --- public functions ---
    '''
    def stop_timer(self):
        self.timethread.stop()
        self.timethread.join()
    
    def start_preview(self):
        self.picam.start_preview(fullscreen=False, window=(100, 100, 800, 600))
        
        if not self.timethread.isAlive():
            self.timethread.start()
        
    def stop_preview(self):
        self.picam.stop_preview()
        self.stop_timer()
        
    def start_recording(self, filename):
        self.picam.start_recording(filename)
        
        if not self.timethread.isAlive():
            self.timethread.start()
        
    def stop_recording(self):
        self.picam.stop_recording()
        self.stop_timer()
        
    def split_recording(self, filename):
        self.picam.split_recording(filename + ".h264")
        
    def wait_recording(self, time):
        self.picam.wait_recording(time)
        
    def capture_still(self):        
        name = self.image_dir + "/" + datetime.now().strftime("%H-%M-%S.jpg")        
        self.picam.capture(name, use_video_port=True)
        return name

class TimeUpdateThread(Thread):
    '''
    class responsible for updating the current time in the video
    (annotation text)
    '''
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
        
    