import pickle
import os.path
from time import sleep
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from threading import Thread
from lib.Logger import Logger

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
ROOTDIR = os.path.dirname(os.path.abspath(__file__))
CREDSPATH = os.path.abspath(os.path.join(ROOTDIR, "../credentials.json"))
TOKENPATH = os.path.abspath(os.path.join(ROOTDIR, "../token.pickle"))

class DriveMonitor(Thread):
    def __init__(self, args):
        Thread.__init__(self)                
        self.logger = Logger(args, type(self).__name__)
        self.keeprunning = True
        self.creds = None
        self._maketoken()
        self.service = self._createservice()        
        
    def _getfiles(self):
        # Call the Drive v3 API
        results = self.service.files().list(q="name = 'videorequest'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            self.logger.verbose("no video request file found")
        else:
            self.logger.verbose("video request file found")
            for item in items:
                print(u'\t{0} ({1})'.format(item['name'], item['id']))
        
    def _createservice(self):
        return build('drive', 'v3', credentials=self.creds)
        
    def _maketoken(self):
        if os.path.exists(TOKENPATH):
            with open(TOKENPATH, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                print(os.path(CREDSPATH))
                if not os.path.exists(CREDSPATH):
                    self.logger.err("credentials.json not found")
                    self.stop()
                    return
                    
                flow = InstalledAppFlow.from_client_secrets_file(CREDSPATH, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKENPATH, 'wb') as token:
                pickle.dump(self.creds, token)
        
    def run(self):
        while self.keeprunning:
            sleep(1)
            self._getfiles()
            
    def stop(self):
        self.keeprunning = False
