import argparse

def createparser():
    parser = argparse.ArgumentParser(description='cat monitor')
    parser.add_argument('-r', '--rotation', action='store', default=0, type=int, choices=[0, 90, 180, 270], help='Camera Image Rotation')
    parser.add_argument('-f', '--fps', action='store', default=25, type=int, help='camera framerate')
    parser.add_argument('-wt', '--width', action='store', default=1920, type=int, help='camera resolution (width)')
    parser.add_argument('-ht', '--height', action='store', default=1080, type=int, help='camera resolution (height)')
    parser.add_argument('-o', '--output', action='store', type=str, help='output file path')
    parser.add_argument('-l', '--length', action='store', default=10, type=int, help='video part length (min)')
    return parser.parse_args()