import sys
import os
import cv2
import path
import glob
import path
import numpy as np
import pyzed.sl as sl
from pathlib import Path

def progress_bar(percent_done, bar_length=50):
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %f%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()

def record_img_data( LeftImg , RightImg , Timestamp ):
    left_view = LeftImg
    right_view = RightImg
    left_img_save_path = os.path.join( path.image0_file_path ,"{0}.png".format(Timestamp))
    right_img_save_path = os.path.join( path.image1_file_path ,"{0}.png".format(Timestamp))
    cv2.imwrite( left_img_save_path , left_view)
    cv2.imwrite( right_img_save_path , right_view)

def record_timestamp( data ):
    timestamp = data 
    with open('times.txt','a') as file_handle:
        file_handle.write("{:.6f}\n".format(timestamp*0.000001))                     
        file_handle.close()

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
            
    ## Setting SVO parameter
    svo_file_path = Path(sys.argv[1])
    camera_params = sl.InitParameters(
        svo_real_time_mode = False,  # Don't convert in realtime
        coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP_X_FWD,
        coordinate_units = sl.UNIT.METER,
        depth_mode = sl.DEPTH_MODE.NONE,
    )
    camera_params.set_from_svo_file(str(svo_file_path))

    ## Open camera
    zed = sl.Camera()
    camera_status = zed.open(camera_params)
    if camera_status != sl.ERROR_CODE.SUCCESS:
        print("Fail to open camera offline!")
        exit(1)
    print("Camera start to work offline!") 
    
    ## Set Tracking params
    track_params = sl.PositionalTrackingParameters(
        _enable_pose_smoothing = True,
        _enable_imu_fusion = True,
        _set_floor_as_origin = False,
        _set_gravity_as_origin = True,
        _set_as_static = False,
        _depth_min_range = 10.0,
    )
    track_status = zed.enable_positional_tracking(track_params)
    if track_status != sl.ERROR_CODE.SUCCESS:
        print("Fail to enable tracking!")
        exit(1)
    print("Successfully enable tracking function!")
    
    ## Create series variables
    pose = sl.Pose()                        # Create pose var
    Transform = sl.Transform()              # Create transform var
    Tranlation = sl.Translation()           # Create translation var
    Quaternion = sl.Orientation()           # Create quaternion var
    LeftImage = sl.Mat()                    # Create Left image mat
    RightImage = sl.Mat()                   # Create right image mat
    
    ## Export data
    runtime_params = sl.RuntimeParameters()
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")
    nb_frames = zed.get_svo_number_of_frames()      # Get total frames number
    
    while True:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            svo_position = zed.get_svo_position()   # Get current frame id 
            
            # Retrieve stereo images and timestamp
            zed.retrieve_image(LeftImage, sl.VIEW.LEFT)
            zed.retrieve_image(RightImage, sl.VIEW.RIGHT)
            left_img = LeftImage.get_data()
            right_img = RightImage.get_data()            
            timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_microseconds()
            record_img_data(left_img , right_img , timestamp)
            record_timestamp(timestamp)
            
            # Display progress
            progress_bar((svo_position + 1) / nb_frames * 100, 30)
            
            # Check if we have reached the end of the video
            if svo_position >= (nb_frames - 1):  # End of SVO
                sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
                break
    ## Close camera    
    zed.close()
    print("Camera stop")