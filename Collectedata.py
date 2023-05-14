import sys
from time import tzname
import ogl_viewer.tracking_viewer as gl
import cv2
import numpy as np
import pyzed.sl as sl


# Modification of coordinate system
def trans_coord_sys_ros_2_opengl( InputTransformObeject ):
    # Interval Transform Matrix between ROS frame and OpenGL frame
    interval_rotation_matrix = np.matrix([
        [ 0 , 0 , 1 ],
        [ 1 , 0 , 0 ],
        [ 0 , 1 , 0 ],
    ])
    
    # Get R and t in ROS coordinate system
    ros_frame_rotation = InputTransformObeject.get_rotation_matrix().r[0:8].reshape(3,3)
    ros_frame_translation = InputTransformObeject.get_translation().get().reshape(1,3)
    
    # Calculate R and t in OpenGl coordinate system
    opengl_frame_rotation = np.dot( ros_frame_rotation , interval_rotation_matrix )
    opengl_frame_translation = np.dot( ros_frame_translation , interval_rotation_matrix) 
    
    # Get translation in OpenGl coordinate system
    tx = opengl_frame_translation[0,0]
    ty = opengl_frame_translation[0,1]
    tz = opengl_frame_translation[0,2]

    # Create Transform Object in OpenGl coordinate system as function return
    OutputTransformObeject = sl.Transform() 
    OutputRotationObeject = sl.Rotation()
    OutputTranslationObeject = sl.Translation()
    OutputMatrix3fObeject = sl.Matrix3f()

    #OutputMatrix3fObeject.r = [opengl_frame_rotation[0,0],opengl_frame_rotation[0,1],opengl_frame_rotation[0,2],\
    #                           opengl_frame_rotation[1,0],opengl_frame_rotation[1,1],opengl_frame_rotation[1,2],\
    #                           opengl_frame_rotation[2,0],opengl_frame_rotation[2,1],opengl_frame_rotation[2,2]]
    
    OutputRotationObeject.init_matrix( OutputMatrix3fObeject )
    OutputTranslationObeject.init_vector( tx , ty , tz )
    OutputTransformObeject.init_rotation_translation( OutputRotationObeject , OutputTranslationObeject )
    
    # return output
    return OutputTransformObeject 
    
# Dispaly image
def left_right_image_viewer( left_img , right_img ):
    left_view = cv2.resize( left_img,( 640,480,) )
    right_view = cv2.resize( right_img,( 640,480) )
    img_horizon_stack = np.hstack(( left_view , right_view ))
    cv2.imshow("left image and right image", img_horizon_stack )

if __name__ == '__main__':
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
            timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE)
            
            # Image viewer
            left_right_image_viewer( left_img , right_img )
            
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
                
                print("timestamp: {0} tx: {1}, ty:  {2}, tz:  {3}\n".format(timestamp.get_microseconds(), tx, ty, tz))
                
                # Prepare for OpenGl viewr
                OpenGLTransform = trans_coord_sys_ros_2_opengl(Transform)
                text_translation = str(( round(tx,3) , round(ty,3) , round(tz,3) ))
                text_rotation = str(( round(rx,3) , round(ry,3) , round(rz,3) ))
                
            viewer.updateData(OpenGLTransform , text_translation , text_rotation ,  pose_status)
                 
    ## Quit
    viewer.exit()
    print("Quit Viewer")
    zed.close()
    print("Camera stop")
