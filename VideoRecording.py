import sys
import os
import pyzed.sl as sl
from signal import signal, SIGINT

def handler(signal_received, frame):
   cam = sl.Camera()
   cam.disable_recording()
   cam.close()
   sys.exit(0)
signal(SIGINT, handler)

def record_camera_intrinsic_parameters( data ):
    [fx,fy,cx,cy] = data[0:4:1]
    [w,h] = data[4:6:1]
    baseline = data[6]
    with open('calib_stereo.txt','a') as file_handle:
        file_handle.write("Pinhole {0} {1} {2} {3} {4}\n".format(fx,fy,cx,cy,0))
        file_handle.write("{0} {1}\n".format(w,h))
        file_handle.write("crop\n")
        file_handle.write("{0} {1}\n".format(w,h))
        file_handle.write("{0}\n".format(baseline))
        file_handle.close()
    
if __name__ == "__main__":
    
    ## Check command
    if not sys.argv or len(sys.argv) != 2:
        print("Only the path of the output SVO file should be passed as argument.")
        exit(1)
    
    ## Clear file generated before
    if(os.path.isfile("calib_stereo.txt")):
        os.remove('calib_stereo.txt')
        print("Calib file deleted successfully")
    else:
        print("Calib file does not exist")
    
    ## Initialize camera
    camera_params = sl.InitParameters(
        camera_resolution = sl.RESOLUTION.HD720,
        camera_fps = 60,
        depth_mode = sl.DEPTH_MODE.NONE,
        coordinate_units = sl.UNIT.METER,
        coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP_X_FWD,
    )
    
    ## Open Camera
    zed = sl.Camera()
    camera_status = zed.open(camera_params)
    if camera_status != sl.ERROR_CODE.SUCCESS:
        print("Fail to open camera")
        exit(1)
    
    ## Get calibration parameters of camera
    calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters
    baseline = calibration_params.get_camera_baseline()
    fx = calibration_params.left_cam.fx
    fy = calibration_params.left_cam.fy
    cx = calibration_params.left_cam.cx
    cy = calibration_params.left_cam.cy
    image_size = zed.get_camera_information().camera_resolution
    w = image_size.width
    h = image_size.height
    wrap = [fx,fy,cx,cy,w,h,baseline]
    record_camera_intrinsic_parameters(wrap)
    
    ## Set recording parameters
    video_output = sys.argv[1]
    recording_param = sl.RecordingParameters(
        video_filename = video_output, 
        compression_mode = sl.SVO_COMPRESSION_MODE.LOSSLESS,
        target_framerate = 60,
    )
    record_status = zed.enable_recording(recording_param)
    if record_status != sl.ERROR_CODE.SUCCESS:
        print("Fail to record video")
        exit(1)
        
    ## Record SVO video
    runtime = sl.RuntimeParameters()
    print("SVO is Recording")
    print("Use Ctrl-C to stop recording")
    frames_recorded = 0
    while True:
        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS :
            frames_recorded += 1
            print("Frame count: " + str(frames_recorded), end="\r")