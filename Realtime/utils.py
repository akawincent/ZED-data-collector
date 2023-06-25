import numpy as np
import pyzed.sl as sl
import cv2

class Tools:
    
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