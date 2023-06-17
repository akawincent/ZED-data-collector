import sys
import os
import glob
import time
import ogl_viewer.tracking_viewer as gl
import cv2
import numpy as np
import pyzed.sl as sl
from record import Recorder
from utils import Tools

if __name__ == '__main__':
    # Clear file generated before
    if( os.path.isfile("groundtruth.tum")):
        os.remove('groundtruth.tum')
        print("Groundtruth file Deleted successfully")
    else:
        print("File does not exist")
        
    for image_file in glob.glob("images/image_0/*"):
        if(image_file.__len__() != 0):
            os.remove(image_file)
            print("delete"+str(image_file))
        else:
            print("image_0 is Already empty")
            
    for image_file in glob.glob("images/image_1/*"):
        if(image_file.__len__() != 0):
            os.remove(image_file)
            print("delete"+str(image_file))
        else:
            print("image_1 is Already empty")
            
    

    ## Initialize camera params
    # Coordinate system is ROS frame
    camera_params = sl.InitParameters(
        camera_resolution = sl.RESOLUTION.HD720,
        camera_fps = 60,
        coordinate_units = sl.UNIT.METER,
        coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP_X_FWD,
    )
    
    ## Open camera
    zed = sl.Camera()
    camera_status = zed.open(camera_params)
    if camera_status != sl.ERROR_CODE.SUCCESS:
        print("Fail to open camera!")
        exit(1)
    print("Camera start to work!")
    
    ## Get calibration parameters of camera
    calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters
    baseline = calibration_params.get_camera_baseline()
    fx = calibration_params.left_cam.fx
    fy = calibration_params.left_cam.fy
    cx = calibration_params.left_cam.cx
    cy = calibration_params.left_cam.cy
    print("Intrinsic parameters:{0} {1} {2} {3}\n".format(fx,fy,cx,cy))
    print("Baseline:{0}\n".format(baseline))
    
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
    print("Successfully initialize!")

    ## Create OpenGL viewer
    camera_info = zed.get_camera_information()
    viewer = gl.GLViewer()
    viewer.init(camera_info.camera_model)
    OpenGLTransform = sl.Transform() 
    text_translation = ""
    text_rotation = ""
    print("Odometry Viewer start!")
    
    ## Record groundtruth pose,stereoscopic img data
    runtime_params = sl.RuntimeParameters()
    pose = sl.Pose()                        # Create pose var
    Transform = sl.Transform()              # Create transform var
    Tranlation = sl.Translation()           # Create translation var
    Quaternion = sl.Orientation()           # Create quaternion var
    LeftImage = sl.Mat()                    # Create Left image mat
    RightImage = sl.Mat()                   # Create right image mat
    
    while viewer.is_available():
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            
            # Get left view img and right view img 
            zed.retrieve_image(LeftImage, sl.VIEW.LEFT)
            zed.retrieve_image(RightImage, sl.VIEW.RIGHT)
            left_img = LeftImage.get_data()
            right_img = RightImage.get_data()
            
            # Get timestamp
            timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_microseconds()
            
            # Image viewer
            Tools.left_right_image_viewer( left_img , right_img )
            Recorder.record_img_data( left_img , right_img, timestamp)
            
            # Retrieve pose 
            pose_status = zed.get_position(
                py_pose = pose,
                reference_frame = sl.REFERENCE_FRAME.WORLD,
            )
            if pose_status == sl.POSITIONAL_TRACKING_STATE.OK:
                
                # Get 4x4 Matrix of Transform (ROS frame)
                Transform = pose.pose_data(sl.Transform())
            
                # Get Translation (ROS frame)
                Tranlation = pose.get_translation(sl.Translation())
                tx = Tranlation.get()[0]
                ty = Tranlation.get()[1]
                tz = Tranlation.get()[2]
                
                # Get quaternion express orientation (ROS frame)
                Quaternion = pose.get_orientation(sl.Orientation())
                qx = Quaternion.get()[0]
                qy = Quaternion.get()[1]
                qz = Quaternion.get()[2]
                qw = Quaternion.get()[3]
                
                # Get rotation vector express orientation (ROS frame)
                rx = Transform.get_rotation_vector()[0]
                ry = Transform.get_rotation_vector()[1]
                rz = Transform.get_rotation_vector()[2]
                
                # Record data
                data_wrapper = [timestamp,tx,ty,tz,qx,qy,qz,qw]
                Recorder.record_pose_data(data_wrapper)
                
                # Prepare for OpenGl viewr
                OpenGLTransform = Tools.trans_coord_sys_ros_2_opengl(Transform)
                text_translation = str(( round(tx,3) , round(ty,3) , round(tz,3) ))
                text_rotation = str(( round(rx,3) , round(ry,3) , round(rz,3) ))
                
            viewer.updateData(OpenGLTransform , text_translation , text_rotation ,  pose_status)
                 
    ## Quit
    viewer.exit()
    print("Quit Viewer")
    zed.close()
    print("Camera stop")
