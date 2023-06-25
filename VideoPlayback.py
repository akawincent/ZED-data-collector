import sys
import pyzed.sl as sl
import cv2

if __name__ == "__main__":
    ## Check command
    if len(sys.argv) != 2:
        print("Please specify path to .svo file.")
        exit()    
    video_path = sys.argv[1]
    print("Reading SVO file: {0}".format( video_path )) 
    
    ## Set SVO video input
    input_type = sl.InputType()
    input_type.set_from_svo_file( video_path )
    camera_params = sl.InitParameters(
        input_t = input_type, 
        svo_real_time_mode = False,
        depth_mode = sl.DEPTH_MODE.NONE
    )
    
    ## Open camera offline
    zed = sl.Camera()
    camera_status = zed.open(camera_params)
    if camera_status != sl.ERROR_CODE.SUCCESS:
        print("Fail to open camera")
        exit(1)
    print("Camera start to work offline !")
    
    ## Playback video
    runtime_params = sl.RuntimeParameters()
    img = sl.Mat()
    key = ''
    print("Quit the video reading:     q\n")
    while key != 113:  # for 'q' key
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(img)
            cv2.imshow("ZED", img.get_data())
            key = cv2.waitKey(1)
        else:
            key = cv2.waitKey(1)
    cv2.destroyAllWindows()
    zed.close()
    print("\nFINISH")
