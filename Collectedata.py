import sys
from time import tzname
import ogl_viewer.tracking_viewer as gl
import cv2
import numpy as np
import pyzed.sl as sl

def trans_coord_sys_ros_2_opengl( InputTransformObeject ):
    # Interval Transform Matrix between ROS frame and OpenGL frame
    interval_rotation_matrix = np.matrix([
        [0,0,1,],
        [1,0,0,],
        [0,1,0,],
    ])
    
    # Get R and t in ROS coordinate system
    ros_frame_rotation = InputTransformObeject.get_rotation_matrix().r[0:8].reshape(3,3)
    ros_frame_translation = InputTransformObeject.get_translation().get().reshape(1,3)
    
    # Calculate R and t in OpenGl coordinate system
    opengl_frame_rotation = np.dot( ros_frame_rotation , interval_rotation_matrix )
    opengl_frame_translation = np.dot( ros_frame_translation , interval_rotation_matrix ) 
    
    # Get translation in OpenGl coordinate system
    tx = np.round( opengl_frame_translation[0,0] , 2)
    ty = np.round( opengl_frame_translation[0,1] , 2)
    tz = np.round( opengl_frame_translation[0,2] , 2)
    
    # Create Transform Object in OpenGl coordinate system as function return
    OutputTransformObeject = sl.Transform() 
    OutputRotationObeject = sl.Rotation()
    OutputTranslationObeject = sl.Translation()
    
    OutputMatrix3fObeject = sl.Matrix3f()
    OutputMatrix3fObeject.r[0:8] = opengl_frame_rotation
    OutputRotationObeject.init_matrix( OutputMatrix3fObeject )
    OutputTranslationObeject.init_vector( tx , ty , tz )
    OutputTransformObeject.init_rotation_translation( OutputRotationObeject , OutputTranslationObeject )
    
    # Get rotation vector in OpenGl coordinate system
    opengl_frame_rotation_vector = OutputTransformObeject.get_rotation_vector()
    rx = round( opengl_frame_rotation_vector[0] , 2 )
    ry = round( opengl_frame_rotation_vector[1] , 2 )
    rz = round( opengl_frame_rotation_vector[2] , 2 )

    # return output
    return OutputTransformObeject , str(( tz, tx, ty )) , str(( rx , ry , rz ))
    

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
    OpenGLTransform = sl.Transform() 
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
                
                # prepare for OpenGl viewr
                [OpenGLTransform , text_translation , text_rotation] = trans_coord_sys_ros_2_opengl(Transform)
            viewer.updateData(OpenGLTransform , text_translation , text_rotation ,  pose_status)
                 
    ## Quit
    viewer.exit()
    print("Quit Viewer")
    zed.close()
    print("Camera stop")
