import argparse


def createparser():
    parser = argparse.ArgumentParser(description='cat monitor')

    parser.add_argument('-r', '--rotation', action='store', default=0,
                        type=int, choices=[0, 90, 180, 270], help='camera image rotation')

    parser.add_argument('-f', '--fps', action='store',
                        default=25, type=int, help='camera framerate')

    parser.add_argument('-wt', '--width', action='store',
                        default=1920, type=int, help='camera resolution (width)')

    parser.add_argument('-ht', '--height', action='store',
                        default=1080, type=int, help='camera resolution (height)')

    parser.add_argument('-o', '--output', action='store',
                        default="./", type=str, help='output file path')

    parser.add_argument('-l', '--length', action='store',
                        default=10, type=int, help='video part length (min)')

    parser.add_argument('-n', '--number', action='store', default=10,
                        type=int, help='number of video clips to store')

    parser.add_argument('--number-images', action='store', default=2,
                        type=int, help='number of images to capture on motion detection')

    parser.add_argument('--image-interval', action='store', default=60, type=int,
                        help='seconds between two detections at which to capture images')

    parser.add_argument('--image-sleep', action='store', default=3, type=int,
                        help='seconds between two captures within one motion detection')

    parser.add_argument('-i', '--polling-interval', action='store',
                        default=300, type=int, help='google drive polling interval')

    parser.add_argument('-p', '--preview', action='store_const',
                        const=True, default=False, help='show preview')

    parser.add_argument('-v', '--verbose', action='store_const',
                        const=True, default=False, help='verbose output')

    parser.add_argument('--debug', action='store_const', const=True,
                        default=False, help='debug mode (disable google drive operations)')

    return parser.parse_args()
