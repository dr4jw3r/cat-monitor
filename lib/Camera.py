import logging
import os.path
import io
import picamera

from datetime import datetime, timedelta
from time import sleep
from threading import Thread

class Camera(object):
    '''
    class for handling the pi camera functionality
    '''
    def __init__(self, args, drive_service, converter):
        self.args = args
        self.logger = logging.getLogger("catmonitor.Camera")
        self.service = drive_service
        self.converter = converter
        self.picam = None
        self._create(args)
        self.timethread = TimeUpdateThread(self.picam)
        self.image_dir = self._get_image_dir()
    
    '''
    --- private functions ---
    '''    
    def _create(self, args):
        self.picam = picamera.PiCamera()
        self.picam.rotation = args.rotation
        self.picam.framerate = args.fps
        self.picam.resolution = (args.width, args.height)            
        self.picam.annotate_text_size = 25 
        self.stream = picamera.PiCameraCircularIO(self.picam, seconds=self.args.length)     
        self.logger.debug("camera created")

    def _get_image_dir(self):        
        image_dir = os.path.abspath("./images")
        if not os.path.exists(image_dir):
            self.logger.debug("creating images directory")
            os.mkdir(image_dir)
            
        return image_dir
        
    def _write_video(self, file_path):
        self.logger.debug("writing video {0}".format(file_path + ".h264"))
        with self.stream.lock:            
            self.stream.copy_to(file_path + '.h264', seconds=self.args.length * 2)
        
        self.converter.enqueue(file_path)
    
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
        
    def start_recording(self):        
        self.picam.start_recording(self.stream, format='h264')
    
        if not self.timethread.isAlive():
            self.timethread.start()
            
        self.logger.debug("recording started")
        
    def stop_recording(self):
        self.picam.stop_recording()
        self.stop_timer()
        
    def wait_recording(self, time):
        self.picam.wait_recording(time)
        
    def capture_still(self):        
        name = self.image_dir + "/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")        
        self.picam.capture(name, use_video_port=True)
        return name
        
    def image_handler(self):
        queue = []
        self.logger.debug("capturing {0} images".format(self.args.number_images))
        for i in range(0, self.args.number_images):
            queue.append(self.capture_still())
            if i != self.args.number_images - 1:                    
                sleep(self.args.image_sleep)
                                            
        self.service.upload(queue, self.service.get_images_dir(), "image/jpeg")        
        
    def video_handler(self):
        trigger_time = datetime.now()
        start_time = trigger_time - timedelta(seconds=self.args.length)
        file_path = os.path.join(self.args.output, start_time.strftime("%Y-%m-%d_%H.%M.%S"))
        self.logger.debug("video handler called, waiting for {0} seconds before write".format(self.args.length))
        self.wait_recording(self.args.length)
        self._write_video(file_path)

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
        
    
