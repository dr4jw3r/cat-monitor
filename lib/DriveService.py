import os.path
import io
import pickle
import logging
import ntpath

from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
ROOTDIR = os.path.dirname(os.path.abspath(__file__))
REQUESTSDIR = os.path.abspath(os.path.join(ROOTDIR, "../requests"))
TOKENPATH = os.path.abspath(os.path.join(ROOTDIR, "../token.pickle"))
CREDSPATH = os.path.abspath(os.path.join(ROOTDIR, "../credentials.json"))

class DriveService(object):
    def __init__(self, args):
        object.__init__(self)
        self.args = args
        self.logger = logging.getLogger("catmonitor.DriveService")
        
        self.creds = None
        self._make_token()
        
        self.service = self._create_service()
        
        self.drive_root_id = self._get_drive_root_directory_id()
        self.drive_images_id = self._get_drive_images_directory_id()
        
        self._create_requests_dir()
        
    def _make_token(self):
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
                
    def _create_requests_dir(self):
        if not os.path.exists(REQUESTSDIR):
            self.logger.debug("creating requests directory")
            os.mkdir(REQUESTSDIR)
                
    def _create_service(self):
        return build('drive', 'v3', credentials=self.creds)
    
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
    
    def _get_drive_root_directory_id(self):
        results = self.service.files().list(q="name = 'catmonitor' and mimeType='application/vnd.google-apps.folder'", pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])

        if len(items) > 0:
            return items[0]['id']
        else:
            self.logger.error("catmonitor directory not found in drive")
            return None
    
    def _get_drive_images_directory_id(self):
        query = "name = 'images' and '{0}' in parents and mimeType='application/vnd.google-apps.folder'".format(self.drive_root_id)
        results = self.service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if len(items) > 0:
            return items[0]['id']
        else:
            self.logger.error("catmonitor images directory not found in drive")
            return None
    
    def download_video_request(self):
        if self.args.debug:
            self.logger.debug("debug mode on, upload called")
            return
        
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
        
    def upload(self, queue, parent_id, mimetype):  
        if self.args.debug:
            self.logger.debug("debug mode on, upload called")
            return
              
        if len(queue) is not 0:
            for item in queue:
                try:
                    self.logger.info("uploading {0}".format(item))
                    meta = {'name': ntpath.basename(item), 'parents': [parent_id]}
                    media = MediaFileUpload(item, mimetype=mimetype, resumable=True, chunksize=-1)                   
                    f = self.service.files().create(body=meta, media_body=media, fields='id').execute()
                    self.logger.info("uploaded with id {0}".format(f.get('id')))
                except:
                    self.logger.error("failed to upload {0}: {1}".format(item, sys.exc_info()[0]))

    def get_requests_dir(self):
        return REQUESTSDIR
    
    def get_root_dir(self):
        return self.drive_root_id
    
    def get_images_dir(self):
        return self.drive_images_id
    
    def get_service(self):
        return self.service
