import os
import subprocess

def convert(filename):
    command = "MP4Box -add {0}.h264 {1}.mp4".format(filename, filename)    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        os.remove(filename + ".h264")
        return 0
    except subprocess.CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
        return 1