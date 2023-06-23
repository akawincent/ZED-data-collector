import os
import cv2
import path
class Recorder:
    # Write data in file
    def record_pose_data( data ):
        timestamp = data[0]
        [tx,ty,tz] = data[1:4:1]
        [qx,qy,qz,qw] = data[4:8:1]
        with open( path.gt_file_path ,'a') as file_handle:
            file_handle.write("{0} {1} {2} {3} {4} {5} {6} {7}\n".format(timestamp,
                                                                     tx,
                                                                     ty,
                                                                     tz,
                                                                     qx,
                                                                     qy,
                                                                     qz,
                                                                     qw))
            file_handle.close()
            
    def record_timestamp(timestamp):
        with open( path.times_file_path ,'a') as file_handle:
            timestamp = str(round(timestamp * 1e-6,6))
            if(timestamp.__len__() == 16):
                timestamp = timestamp + str('0')
            file_handle.write("{0}\n".format(timestamp))
            file_handle.close()       
            
    # Save image
    def record_img_data( LeftImg , RightImg , Timestamp ):
        left_view = LeftImg
        right_view = RightImg
        left_img_save_path = os.path.join( path.image0_file_path ,"{0}.jpg".format(Timestamp))
        right_img_save_path = os.path.join( path.image1_file_path ,"{0}.jpg".format(Timestamp))
        cv2.imwrite( left_img_save_path , left_view)
        cv2.imwrite( right_img_save_path , right_view)