# cat-monitor

### run command:

```python main.py -r 180 -l 10 -n 6 -o ./output -wt 640 -ht 480 -i 600 --image-interval 60 --number-images 2 --image-sleep 2 -v --debug```


<pre>
optional arguments:\
    -h,                     --help                                  show this help message and exit
    -r {0,90,180,270},      --rotation {0,90,180,270}               Camera Image Rotation
    -f FPS,                 --fps FPS                               camera framerate
    -wt WIDTH,              --width WIDTH                           camera resolution (width)
    -ht HEIGHT,             --height HEIGHT                         camera resolution (height)
    -o OUTPUT,              --output OUTPUT                         output file path
    -l LENGTH,              --length LENGTH                         video part length (min)
    -n NUMBER,              --number NUMBER                         number of video clips to store
    -i POLLING_INTERVAL,    --polling-interval POLLING_INTERVAL     google drive polling interval
    -p,                     --preview                               show preview
    -v,                     --verbose                               verbose output
                            --number-images NUMBER_IMAGES           number of images to capture on motion detection
                            --image-interval IMAGE_INTERVAL         seconds between two detections at which to capture images
                            --image-sleep IMAGE_SLEEP               seconds between two captures within one motion detection
                            --debug                                 debug mode (disable google drive operations)
</pre>

### Google Drive Request Files

#### videorequest

Contents should contain a comma-separated list of indexes of videos to upload.
Indexes start with 1 (most recent video)

#### listfiles
Blank file
