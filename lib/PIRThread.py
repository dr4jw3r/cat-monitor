import logging

from threading import Thread
from time import sleep
from timeit import default_timer as timer
from gpiozero import MotionSensor

from lib.DriveService import DriveService

PIR_PIN = 4

class PIRThread(Thread):
    def __init__(self, capture_still, args, service):
        Thread.__init__(self)
        self.logger = logging.getLogger("catmonitor.PIRThread")
        self.args = args
        self.keeprunning = True
        self.pir = None
        self._gpio_setup()
        self.capture_still = capture_still
        self.service = service
        self.timeout = 0
        
    def _gpio_setup(self):        
        self.pir = MotionSensor(PIR_PIN)
        self.pir.when_motion = self._motion_start
        self.pir.when_no_motion = self._motion_stop
    
    def _motion_start(self):
        queue = []
        print(timer() - self.timeout)
        if self.timeout is 0 or timer() - self.timeout > self.args.image_interval:
            self.timeout = timer()
            self.logger.debug("motion detected, capturing {0} images".format(self.args.number_images))
            for i in range(0, self.args.number_images):
                queue.append(self.capture_still())
                if i != self.args.number_images - 1:                    
                    sleep(self.args.image_sleep)
                                            
            self.service.upload(queue, self.service.get_images_dir(), "image/jpeg")
        else:
            self.logger.debug("motion detected, interval not passed")

    def _motion_stop(self):
        self.logger.debug("motion stopped")
        
    def stop(self):
        pass
        
