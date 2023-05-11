import sys
import ogl_viewer.tracking_viewer as gl
import cv2
import numpy as np
import pyzed.sl as sl

def trans_coord_sys_ros_2_opengl( _ros_frame ):
    # Interval Transform Matrix between ROS frame and OpenGL frame
    t_matrix = np.matrix([[0,0,1,0],
                           [1,0,0,0],
                           [0,1,0,0],
                           [0,0,0,1]])
    _opengl_frame = np.dot(_ros_frame , t_matrix)
    tx = round(_opengl_frame[0,3],3)
    ty = round(_opengl_frame[1,3],3)
    tz = round(_opengl_frame[2,3],3)
    return str((tx, ty, tz))
    

if __name__ == '__main__':
    ## Initialize camera params
    # Coordinate system is ROS frame
    camera_params = sl.InitParameters(
        camera_resolution = sl.RESOLUTION.HD720,
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
    text_translation = ""
    text_rotation = ""
    print("Viewer start!")
    
    ## Record groundtruth pose,stereoscopic img data
    runtime_params = sl.RuntimeParameters()
    pose = sl.Pose()                        # Create pose var
    Transform = sl.Transform()              # Create transform var
    Tranlation = sl.Translation()           # Create translation var
    Quaternion = sl.Orientation()           # Create quaternion var
    
    while viewer.is_available():
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Retrieve pose 
            pose_status = zed.get_position(
                py_pose = pose,
                reference_frame = sl.REFERENCE_FRAME.WORLD,
            )
            if pose_status == sl.POSITIONAL_TRACKING_STATE.OK:
                
                #Get 4x4 Matrix of Transform (ROS frame)
                Transform = pose.pose_data(sl.Transform())
            
                # Get Translation (ROS frame)
                Tranlation = pose.get_translation(sl.Translation())
                tx = round(Tranlation.get()[0],3)
                ty = round(Tranlation.get()[1],3)
                tz = round(Tranlation.get()[2],3)
                
                # Get quaternion express orientation (ROS frame)
                Quaternion = pose.get_orientation(sl.Orientation())
                qx = round(Quaternion.get()[0],3)
                qy = round(Quaternion.get()[1],3)
                qz = round(Quaternion.get()[2],3)
                qw = round(Quaternion.get()[3],3)
                
                # Get rotation vector (ROS frame)
                rotation = pose.get_rotation_vector()
                r1 = round(rotation[0], 0)
                r2 = round(rotation[0], 1)
                r3 = round(rotation[0], 2)
                
                # text
                Transform * 
                text_translation = str((tx, ty, tz))
                text_rotation = str((r1,r2,r3))
                
            viewer.updateData(Transform , text_translation , text_rotation ,  pose_status)
                 
    ## Quit
    viewer.exit()
    print("Quit Viewer")
    zed.close()
    print("Camera stop")
