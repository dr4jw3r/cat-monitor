import pickle
import os
import io
import logging
from datetime import datetime
from time import sleep
from threading import Thread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
ROOTDIR = os.path.dirname(os.path.abspath(__file__))
CREDSPATH = os.path.abspath(os.path.join(ROOTDIR, "../credentials.json"))
TOKENPATH = os.path.abspath(os.path.join(ROOTDIR, "../token.pickle"))
REQUESTSDIR = os.path.abspath(os.path.join(ROOTDIR, "../requests"))

class DriveMonitor(Thread):
    def __init__(self, args):
        Thread.__init__(self)
        self.args = args
        self.logger = logging.getLogger("catmonitor.DriveMonitor")
        self.keeprunning = True
        self.creds = None
        self.counter = 0
        self._maketoken()
        self.service = self._createservice()
        self.drivedirid = self._getdirectoryid()
        self.uploadqueue = []

        if not os.path.exists(REQUESTSDIR):
            self.logger.debug("creating requests directory")
            os.mkdir(REQUESTSDIR)

    def _getdirectoryid(self):
        results = self.service.files().list(q="name = 'catmonitor' and mimeType='application/vnd.google-apps.folder'", pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])

        if len(items) > 0:
            return items[0]['id']
        else:
            self.logger.error("catmonitor directory not found in drive")
            return None

    def _parse(self):
        files = [file for file in os.listdir(REQUESTSDIR) if not file.endswith("_parsed")]
        while len(files) is not 0:
            file = files.pop(0)
            self.logger.info("found request file {0}".format(file))
            filepath = os.path.join(REQUESTSDIR, file)

            with open(filepath, 'rb') as f:
                vidindex = list(map(int, f.read().split(',')))

            outpath = os.path.abspath(self.args.output)
            vids = [f for f in os.listdir(outpath) if os.path.isfile(os.path.join(outpath, f))]
            vids = [f for f in vids if f.endswith(".mp4")]
            vids.sort(key=lambda x: -os.path.getmtime(outpath + "/" + x))

            for i in vidindex:
                if 0 <= i - 1 < len(vids):
                    if vids[i - 1] not in self.uploadqueue:
                        self.uploadqueue.append(vids[i - 1])

            self.logger.debug("{0} parsed, renaming".format(file))
            os.rename(filepath, filepath + "_parsed")
            
        
    def _download(self, item):
        filename = 'videorequest_' + datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        request = self.service.files().get_media(fileId=item['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            self.logger.info("Download %d%%." % int(status.progress() * 100))                    
            
        with open(os.path.join(REQUESTSDIR, filename),'wb') as out:
            out.write(fh.getvalue())
            
        fh.close()
        self.service.files().delete(fileId=item['id']).execute()        
        
    def _upload(self):
        if len(self.uploadqueue) is not 0:
            file = self.uploadqueue.pop(0)
            self.logger.info("uploading {0}".format(file))
            meta = {'name': file, 'parents': [self.drivedirid]}
            filepath = os.path.join(self.args.output, file)                
            media = MediaFileUpload(filepath, mimetype='video/mp4', resumable=True, chunksize=-1)                   
            f = self.service.files().create(body=meta, media_body=media, fields='id').execute()
            self.logger.info("uploaded with id {0}".format(f.get('id')))
        
    def _getfiles(self):
        # Call the Drive v3 API
        results = self.service.files().list(q="name = 'videorequest'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            self.logger.debug("no video request file found")
        else:
            self.logger.info("video request file found")
            for item in items:
                self.logger.debug(u'\t{0} ({1})'.format(item['name'], item['id']))
                self._download(item)               
        
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
                if not os.path.exists(CREDSPATH):
                    self.logger.error("credentials.json not found")
                    self.stop()
                    return
                    
                flow = InstalledAppFlow.from_client_secrets_file(CREDSPATH, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKENPATH, 'wb') as token:
                pickle.dump(self.creds, token)
        
    def run(self):
        while self.keeprunning:
            if self.counter > self.args.polling_interval:
                self._getfiles()
                self.counter = 0
            else:                
                self.counter += 1
                self._parse()
                self._upload()
                    
            sleep(1)            
            
    def stop(self):
        self.keeprunning = False
