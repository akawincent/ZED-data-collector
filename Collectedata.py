import sys
from time import tzname
import ogl_viewer.tracking_viewer as gl
import cv2
import numpy as np
import pyzed.sl as sl

def trans_coord_sys_ros_2_opengl( _ros_frame ):
    # Interval Transform Matrix between ROS frame and OpenGL frame
    _matrix_t = np.matrix([[0,0,1,0],
                           [1,0,0,0],
                           [0,1,0,0],
                           [0,0,0,1]])
    _opengl_frame = np.zeros((4,4))
    
    print(_ros_frame.m())
    
    #_opengl_frame = np.dot(_ros_frame.m() , _matrix_t)
    #print(_opengl_frame)
    
    # Get translation (OpenGl frame)
    # tx = round(_opengl_frame[0,3],3)
    # ty = round(_opengl_frame[1,3],3)
    # tz = round(_opengl_frame[2,3],3)
    
    # # Get 3x3 Rotation Matrix
    # _matrix_rotation = np.matrix(_opengl_frame[0:2,0],
    #                              _opengl_frame[0:2,1],
    #                              _opengl_frame[0:2,2])
    
    # # Use Rodrigues rotation formula to get raotaion vector (OpenGL frame)
    # theta = np.arccos(0.5 * (np.trace(_matrix_rotation) - 1))
    # rotation_vector = 0.5 / np.sin(theta) * (_matrix_rotation - _matrix_rotation.transpose())
    # rx = round(rotation_vector[2,1],3)
    # ry = round(rotation_vector[0,2],3)
    # rz = round(rotation_vector[1,0],3)
    # return _opengl_frame , str(( tx, ty, tz )) , str(( rx , ry , rz ))
    

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
    opengl_trans = np.zeros((4,4))
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
                
                # text
                trans_coord_sys_ros_2_opengl(Transform)
                #[opengl_trans , text_translation , text_rotation] = trans_coord_sys_ros_2_opengl(Transform)

                
            viewer.updateData(Transform , text_translation , text_rotation ,  pose_status)
                 
    ## Quit
    viewer.exit()
    print("Quit Viewer")
    zed.close()
    print("Camera stop")
