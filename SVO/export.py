import sys
import os
import cv2
import path
import glob
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
    for image_file in glob.glob( path.image0_file_path + '*'):
        if(image_file.__len__() != 0):
            os.remove(image_file)
            print("delete"+str(image_file))
        else:
            print("image_0 is Already empty")
    for image_file in glob.glob(path.image0_file_path + '*'):
        if(image_file.__len__() != 0):
            os.remove(image_file)
            print("delete"+str(image_file))
        else:
            print("image_1 is Already empty")
            
    ## Get command parameters
    