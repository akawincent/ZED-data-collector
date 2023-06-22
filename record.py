import os
import cv2

class Recorder:
    
    # Write data in file
    def record_pose_data( data ):
        timestamp = data[0]
        [tx,ty,tz] = data[1:4:1]
        [qx,qy,qz,qw] = data[4:8:1]
        with open('groundtruth.tum','a') as file_handle:
            file_handle.write("{0} {1} {2} {3} {4} {5} {6} {7}\n".format(timestamp,
                                                                     tx,
                                                                     ty,
                                                                     tz,
                                                                     qx,
                                                                     qy,
                                                                     qz,
                                                                     qw))
            file_handle.close()
            
    # Save image
    def record_img_data( LeftImg , RightImg , Timestamp ):
        left_view = LeftImg
        right_view = RightImg
        left_img_save_path = os.path.join("./images/image_0","{0}.jpg".format(Timestamp))
        right_img_save_path = os.path.join("./images/image_1","{0}.jpg".format(Timestamp))
        cv2.imwrite( left_img_save_path , left_view)
        cv2.imwrite( right_img_save_path , right_view)