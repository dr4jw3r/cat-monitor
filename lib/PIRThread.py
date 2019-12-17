import logging

from threading import Thread
from time import sleep
from timeit import default_timer as timer
from gpiozero import MotionSensor

from lib.DriveService import DriveService

PIR_PIN = 4

class PIRThread(Thread):
    '''
    class responsible for working with the PIR sensor
    '''
    def __init__(self, capture_still, args, service):
        '''
        capture_still is a function from the camera
        '''
        Thread.__init__(self)
        self.logger = logging.getLogger("catmonitor.PIRThread")
        self.args = args
        self.keep_running = True
        self.pir = None
        self._gpio_setup()
        self.capture_still = capture_still
        self.service = service
        self.timeout = 0
        self.subscribers = []

    '''
    --- private functions ---
    '''  
    def _gpio_setup(self):        
        self.pir = MotionSensor(PIR_PIN)
        self.pir.when_motion = self._motion_start
        self.pir.when_no_motion = self._motion_stop
    
    def _motion_start(self):
        trigger_time = timer()
        for i in range(0, len(self.subscribers)):            
            (sub_name, sub_handler, sub_interval, sub_last_called) = self.subscribers[i]
            if sub_last_called == 0 or trigger_time - sub_last_called > sub_interval:
                self.subscribers[i] = (sub_name, sub_handler, sub_interval, trigger_time)
                thread = Thread(target=lambda: sub_handler())
                thread.start()
                sleep(0.1)
            
    def _motion_stop(self):
        self.logger.debug("motion stopped")
        
    def subscribe(self, name, handler, interval):
        self.subscribers.append((name, handler, interval, 0))
        
    def unsubscribe(self, name):
        subscriber = [itm for itm in enumerate(self.subscribers) if itm[1][0] == name]
        
        if not subscriber:
            self.logger.debug("subscriber {0} not found".format(name))
        else:
            self.subscribers.pop(subscriber[0][0])
            self.logger.debug("{0} unsubscribed".format(name))
            
    def stop(self):
        pass
        
