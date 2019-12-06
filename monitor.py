from time import sleep
from datetime import datetime
from lib.ArgumentParser import createparser
from lib.Camera import Camera
from lib.Converter import convert

def run():    
    args = createparser()    
    camera = Camera(args)
    
    camera.start_preview()
    sleep(args.length)
    camera.stop_preview()
    
    filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    #convert(filename)

    return 0

if __name__ == "__main__":
    exit(run())

#MP4Box -add 1.h264 1.mp4