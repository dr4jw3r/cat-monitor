import logging

from datetime import datetime

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
        self.file_name = self._create_file_name()
        self.drive_service = DriveService(args)
        self.converter = None
        self.file_monitor = None
        self.drive_monitor = None
        self.pir = None
        self.camera = Camera(args)

    '''
    --- private functions ---
    '''
    def _create_file_name(self):
        '''
        creates a file name for the recording
        '''
        return self.args.output + "/" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

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
        self.pir = PIRThread(self.camera.capture_still,
                             self.args, self.drive_service)
        self.pir.start()
        self.logger.debug("pir thread started")

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

            self.logger.info("starting recording: " + self.file_name)
            self.camera.start_recording(self.file_name + ".h264")
            self.camera.wait_recording(self.clip_length)

            while True:
                self.previous_file = self.file_name
                self.file_name = self._create_file_name()

                self.logger.info("splitting recording: " + self.file_name)
                self.camera.split_recording(self.file_name)

                self.converter.enqueue(self.previous_file)
                self.camera.wait_recording(self.clip_length)

            self.camera.stop_recording()
            # enqueue the last recorded file
            self.converter.enqueue(self.file_name)
            self._stop_threads()

            if self.args.preview:
                self.camera.stop_preview()

            return 0

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.converter.enqueue(self.file_name)
            self._stop_threads()
            self.camera.stop_timer()
