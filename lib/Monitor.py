import logging
from datetime import datetime
from lib.Converter import Converter
from lib.FileMonitor import FileMonitor
from lib.Camera import Camera
from lib.DriveService import DriveService
from lib.DriveMonitor import DriveMonitor
from lib.PIRThread import PIRThread

class Monitor(object):
    def __init__(self, args):
        self.args = args
        self.logger = logging.getLogger('catmonitor.Monitor')
        self.cliplength = args.length * 60
        self.previousfile = ""
        self.filename = self.createfilename()
        self.drive_service = DriveService(args)
        self.converter = None
        self.filemonitor = None
        self.drivemonitor = None
        self.pir = None
        self.camera = Camera(args)
        
    def createfilename(self):
        return self.args.output + "/" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    
    def startthreads(self):
        self.filemonitor = FileMonitor(self.args)        
        self.filemonitor.start()
        self.logger.debug("file monitor started")
        self.converter = Converter(self.args)
        self.converter.start()
        self.logger.debug("converter started")
        self.drivemonitor = DriveMonitor(self.drive_service, self.args)
        self.drivemonitor.start()
        self.logger.debug("drive monitor started")
        self.pir = PIRThread(self.camera.capture_still, self.args, self.drive_service)
        self.pir.start()
        self.logger.debug("pir thread started")

    def stopthreads(self):
        self.filemonitor.stop()
        self.filemonitor.join()
        self.converter.stop()
        self.converter.join()
        self.drivemonitor.stop()
        self.drivemonitor.join()
        self.pir.stop()
        self.pir.join()
        
    def start(self):
        try:            
            self.startthreads()            
            
            if self.args.preview:
                self.camera.start_preview()
            
            self.logger.info("starting recording: " + self.filename)
            self.camera.start_recording(self.filename + ".h264")    
            self.camera.wait_recording(self.cliplength)
        
            while True:
                self.previousfile = self.filename
                self.filename = self.createfilename()
                
                self.logger.info("splitting recording: " + self.filename)
                self.camera.split_recording(self.filename)
                                
                self.converter.enqueue(self.previousfile)
                self.camera.wait_recording(self.cliplength)
        
            self.camera.stop_recording()            
            self.converter.enqueue(self.filename)
            self.stopthreads()
        
            if self.args.preview:
                self.camera.stop_preview()
                
            return 0
        
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            self.converter.enqueue(self.filename)
            self.stopthreads()
            self.camera.stoptimer()
