from enum import Enum

class RequestFile(Enum):
    '''
    enum to keep track of possible request file types
    '''
    VideoRequest = 1
    ListFilesRequest = 2
