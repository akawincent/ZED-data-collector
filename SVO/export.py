import sys
import os
import cv2
import path
import numpy as np
import pyzed.sl as sl

def progress_bar(percent_done, bar_length=50):
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %f%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()
    
if __name__ == "__main__":
    ## Clear file generated before
    if( os.path.isfile(path.times_file_path)):
        os.remove(path.times_file_path)
        print("Times file Deleted successfully")
    else:
        print("Times file does not exist")
    