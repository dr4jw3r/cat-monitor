from time import sleep
from datetime import datetime
from lib.ArgumentParser import createparser
from lib.Camera import Camera
from lib.Converter import Converter

def createfilename(outputdir):
    return outputdir + "/" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

def run():    
    args = createparser()
    
    cliplength = args.length * 60
    outputdir = args.output
    
    camera = Camera(args)
    converter = Converter()
    converter.start()
    
    filename = createfilename(outputdir)    
    previousfile = ""
    
    if args.preview:
        camera.start_preview()
        
    print("Staring recording: " + filename)
    camera.start_recording(filename + ".h264")    
    camera.wait_recording(cliplength)
    
    for i in range(0, args.number):
        previousfile = filename
        filename = createfilename(outputdir)
        print("Splitting recording: " + filename)
        camera.split_recording(filename)
        print("Enqueueing: " + previousfile)
        converter.enqueue(previousfile)
        camera.wait_recording(cliplength)
    
    camera.stop_recording()
    print("Enqueueing: " + filename)
    converter.enqueue(filename)
    converter.stop()
    converter.join()
    
    if args.preview:
        camera.stop_preview()        

    return 0

if __name__ == "__main__":
    try:
        exit(run())
    except KeyboardInterrupt:
        print("Caught KB interrupt")
        exit(1)