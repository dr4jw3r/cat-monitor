import logging

from datetime import datetime
from time import sleep

from lib.Converter import Converter
from lib.FileMonitor import FileMonitor
from lib.Camera import Camera
from lib.DriveService import DriveService
from lib.DriveMonitor import DriveMonitor
from lib.PIRThread import PIRThread


class Monitor(object):
    '''
    main class which runs other threads and coordinates
    the communication
    '''
    def __init__(self, args):
        self.args = args
        self.logger = logging.getLogger('catmonitor.Monitor')
        self.clip_length = args.length * 60 # multiply by 60 to convert to minutes
        self.previous_file = ""
        self.drive_service = DriveService(args)
        self.converter = None
        self.file_monitor = None
        self.drive_monitor = None
        self.pir = None

    '''
    --- private functions ---
    '''

    def _start_threads(self):
        '''
        starts monitoring threads
        '''
        self.file_monitor = FileMonitor(self.args)
        self.file_monitor.start()
        self.logger.debug("file monitor started")

        self.converter = Converter(self.args)
        self.converter.start()
        self.logger.debug("converter started")

        self.drive_monitor = DriveMonitor(self.drive_service, self.args)
        self.drive_monitor.start()
        self.logger.debug("drive monitor started")
        
        self.camera = Camera(self.args, self.drive_service, self.converter)
        
        self.pir = PIRThread(self.camera.capture_still,
                             self.args, self.drive_service)
        self.pir.start()
        self.logger.debug("pir thread started")
        
        self.pir.subscribe("camera.image", self.camera.image_handler, self.args.image_interval)
        
        # add 1 second for safety
        self.pir.subscribe("camera.video", self.camera.video_handler, (self.args.length + 1))

    def _stop_threads(self):
        '''
        safely stops and join running threads
        '''
        self.file_monitor.stop()
        self.file_monitor.join()
        self.converter.stop()
        self.converter.join()
        self.drive_monitor.stop()
        self.drive_monitor.join()
        self.pir.stop()
        self.pir.join()

    '''
    --- public functions ---
    '''
    def start(self):
        '''
        monitor entry point
        '''
        try:
            self._start_threads()

            if self.args.preview:
                self.camera.start_preview()

            # start recording to circular buffer
            self.camera.start_recording()
            
            # program loop
            while True:
                sleep(1)
           
            # cleanup
            self.camera.stop_recording()
            self._stop_threads()

            if self.args.preview:
                self.camera.stop_preview()

            return 0

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self._stop_threads()
            self.camera.stop_recording()
