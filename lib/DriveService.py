import os.path
import io
import pickle
import logging
import ntpath
import sys

from datetime import datetime, timedelta

from lib.RequestFile import RequestFile

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
    '''
    google drive service
    '''
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
        
    '''
    --- private functions ---
    '''
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
    
    def _delete(self, file_id):
        try:
            self.service.files().delete(fileId=file_id).execute()
            self.logger.debug("{0} deleted".format(file_id))
            return True
        except:
            self.logger.error("failed to delete {0}: {1}".format(file_id, sys.exc_info()[0]))
            return False
    
    def _download(self, file_id):
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with io.BytesIO() as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    self.logger.info("Download %d%%." % int(status.progress() * 100))                    
                    
                
                return fh.getvalue()
        except:
            self.logger.error("failed to download {0}: {1}".format(file_id, sys.exc_info()[0]))
    
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
    
    def _get_file_id(self, file_name):
        try:            
            results = self.service.files().list(q="name = '{0}'".format(file_name), pageSize=1, fields="files(id, name)").execute()
            items = results.get('files', [])
            
            if not items:
                self.logger.debug("no {0} file found".format(file_name))
                return None
            else:
                self.logger.debug("{0} file found".format(file_name))
                return items[0]['id']
        except:
            self.logger.error("failed to get file id {0}: {1}".format(file_name, sys.exc_info()[0]))
            return None
            
    
    def _handle_file(self, file_type, file_id, contents):
        if file_type is RequestFile.VideoRequest:
            file_name = "videorequest_{0}".format(datetime.now().strftime("%Y-%m-%d_%H-%M_%S"))
            file_path = os.path.join(REQUESTSDIR, file_name)            
            with open(file_path, 'wb') as outfile:
                outfile.write(contents)
                
            self._delete(file_id)
            
        elif file_type is RequestFile.ListFilesRequest:
            lines = []
            files = [f for f in os.listdir(self.args.output) if os.path.isfile(os.path.join(self.args.output, f))]
            files = [f for f in files if f.endswith(".mp4")]      

            if len(files) > 0:
                files.sort(key=lambda x: os.path.getmtime(self.args.output + "/" + x))
                
                for i in range(0, len(files)):
                    index = i + 1
                    index_str = "0" + str(index) if index < 10 else str(index)
                    formatted = files[i].replace('.mp4', '')
                    start_date = datetime.strptime(formatted, '%Y-%m-%d_%H.%M.%S')
                    end_date = start_date + timedelta(seconds=self.args.length * 2)
                    start = start_date.strftime('%Y-%m-%d %H:%M:%S')
                    end = end_date.strftime('%Y-%m-%d %H:%M:%S')
                    lines.append('[{0}] [{1} -> {2}]\n'.format(index_str, start, end))
                    
                with open('videos.txt', 'wb') as outfile:
                    outfile.writelines(lines)
                    
                uploaded = self.upload([os.path.abspath('videos.txt')], self.drive_root_id, 'text/plain')
                
                if uploaded:
                    os.remove('videos.txt')
                    self._delete(file_id)

    '''
    --- public functions ---
    '''          
    def check_video_request(self):
        if self.args.debug:
            self.logger.debug("debug mode on, check video request called")
            return
        
        file_id = self._get_file_id("videorequest.txt") 
        
        if file_id is not None:
            contents = self._download(file_id)
            self._handle_file(RequestFile.VideoRequest, file_id, contents)
        
    def check_list_files_request(self):
        if self.args.debug:
            self.logger.debug("debug mode on, check list files request called")
            return
            
        file_id = self._get_file_id("listfiles")
        
        if file_id is not None:
            self._handle_file(RequestFile.ListFilesRequest, file_id, None)
        
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
                    return False
                    
            return True

    def get_requests_dir(self):
        return REQUESTSDIR
    
    def get_root_dir(self):
        return self.drive_root_id
    
    def get_images_dir(self):
        return self.drive_images_id
    
    def get_service(self):
        return self.service
