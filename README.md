# cat-monitor

### run command:

```python init.py -r 180 -l 10 -n 6 -o ./output -wt 640 -ht 480 -i 600 --image-interval 60 --number-images 2 --image-sleep 2 -v --debug```


optional arguments:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-h, --help show this help message and exit\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-r {0,90,180,270}, --rotation {0,90,180,270} Camera Image Rotation\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-f FPS, --fps FPS     camera framerate\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-wt WIDTH, --width WIDTH camera resolution (width)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-ht HEIGHT, --height HEIGHT camera resolution (height)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-o OUTPUT, --output OUTPUT output file path\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-l LENGTH, --length LENGTH video part length (min)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-n NUMBER, --number NUMBER number of video clips to store\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--number-images NUMBER_IMAGES number of images to capture on motion detection\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--image-interval IMAGE_INTERVAL seconds between two detections at which to capture images\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--image-sleep IMAGE_SLEEP seconds between two captures within one motion detection\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-i POLLING_INTERVAL, --polling-interval POLLING_INTERVAL google drive polling interval\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-p, --preview         show preview\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-v, --verbose         verbose output\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--debug               debug mode (disable google drive operations)
