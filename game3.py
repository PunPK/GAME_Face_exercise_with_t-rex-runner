import cv2 as cv
import cv2 as cv2
import mediapipe as mp
import time
import utils, math
import pandas as pd
# Fast Ai
from fastbook import *
import PIL

# variables 
frame_counter = 0
CEF_COUNTER = 0
TOTAL_BLINKS = 0
# constants
CLOSED_EYES_FRAME = 3
start = 0
end = 0
ch = 0

FONTS = cv.FONT_HERSHEY_COMPLEX

# Face bounder indices 
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
# Lips indices for landmarks
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39, 37, 0, 267, 269, 270, 409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78]
# Left eyes indices 
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
# Right eyes indices
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]  

map_face_mesh = mp.solutions.face_mesh

def landmarksDetection(img, results, draw=False):
    img_height, img_width = img.shape[:2]
    # List of (x,y) coordinates
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw:
        [cv.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    # Returning the list of tuples for each landmark 
    return mesh_coord

# Euclaidean distance 
def euclaideanDistance(point, point1):
    x, y = point
    x1, y1 = point1
    distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
    return distance
    
# FACE detection function 
def detectFACE(img, landmarks, FACE):
    # FACE coordinates
    FACE_points = [landmarks[idx] for idx in FACE]

    # Find the minimum and maximum x and y coordinates of the FACE points
    x_values = [point[0] for point in FACE_points]
    y_values = [point[1] for point in FACE_points]
    FACE_x_min = min(x_values)
    FACE_x_max = max(x_values)
    FACE_y_min = min(y_values)
    FACE_y_max = max(y_values)

    # Increase width and height of the rectangle
    width_increase = 25
    height_increase = 15
    FACE_x_min -= width_increase
    FACE_x_max += width_increase
    FACE_y_min -= height_increase
    FACE_y_max += height_increase

    faceRatio = euclaideanDistance((FACE_y_max, FACE_y_min), (FACE_y_min, FACE_y_max))
    re_face = faceRatio

    # Draw rectangle around lips
    cv.rectangle(img, (FACE_x_min, FACE_y_min), (FACE_x_max, FACE_y_max), utils.GREEN, 2)

    return re_face

def detecteye(img, landmarks, right_indices, left_indices):

    # Right eye
    # Horizontal line 
    rh_right = landmarks[right_indices[0]]
    rh_left = landmarks[right_indices[8]]
    # Vertical line 
    rv_top = landmarks[right_indices[12]]
    rv_bottom = landmarks[right_indices[4]]

    # Left eye 
    # Horizontal line 
    lh_right = landmarks[left_indices[0]]
    lh_left = landmarks[left_indices[8]]
    # Vertical line 
    lv_top = landmarks[left_indices[12]]
    lv_bottom = landmarks[left_indices[4]]

    rhDistance = euclaideanDistance(rh_right, rh_left)
    rvDistance = euclaideanDistance(rv_top, rv_bottom)

    lvDistance = euclaideanDistance(lv_top, lv_bottom)
    lhDistance = euclaideanDistance(lh_right, lh_left)

    reRatio = rhDistance/rvDistance
    leRatio = lhDistance/lvDistance


    # Draw lines on eyes 
    # Right eye
    eye_right_x_min = min([landmarks[idx][0] for idx in RIGHT_EYE])
    eye_right_x_max = max([landmarks[idx][0] for idx in RIGHT_EYE])
    eye_right_y_min = min([landmarks[idx][1] for idx in RIGHT_EYE])
    eye_right_y_max = max([landmarks[idx][1] for idx in RIGHT_EYE])

    # Increase width of rectangle
    width_increase = 20
    eye_right_x_min -= width_increase
    eye_right_x_max += width_increase
    eye_right_y_min -= width_increase
    eye_right_y_max += width_increase

    # Left eye
    eye_left_x_min = min([landmarks[idx][0] for idx in LEFT_EYE])
    eye_left_x_max = max([landmarks[idx][0] for idx in LEFT_EYE])
    eye_left_y_min = min([landmarks[idx][1] for idx in LEFT_EYE])
    eye_left_y_max = max([landmarks[idx][1] for idx in LEFT_EYE])

    # Increase width of rectangle
    eye_left_x_min -= width_increase
    eye_left_x_max += width_increase
    eye_left_y_min -= width_increase
    eye_left_y_max += width_increase

    # Draw rectangle around right eye
    cv.rectangle(img, (eye_right_x_min, eye_right_y_min), (eye_right_x_max, eye_right_y_max), utils.GREEN, 2)
    cv.rectangle(img, (eye_left_x_min, eye_left_y_min), (eye_left_x_max, eye_left_y_max), utils.GREEN, 2)
    cv.polylines(img,  [np.array([mesh_coords[p] for p in LEFT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
    cv.polylines(img,  [np.array([mesh_coords[p] for p in RIGHT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)

    # Left eye
    eye_left_x_min = min([landmarks[idx][0] for idx in LEFT_EYE])
    eye_left_x_max = max([landmarks[idx][0] for idx in LEFT_EYE])
    eye_left_y_min = min([landmarks[idx][1] for idx in LEFT_EYE])
    eye_left_y_max = max([landmarks[idx][1] for idx in LEFT_EYE])

    # Increase width of rectangle
    eye_left_x_min -= width_increase
    eye_left_x_max += width_increase
    eye_left_y_min -= width_increase
    eye_left_y_max += width_increase

    re_right_m = reRatio
    re_left_m = leRatio

    return(re_right_m,re_left_m)

def detectYawn(img, landmarks, LIPS):
    # Lips coordinates
    lips_points = [landmarks[idx] for idx in LIPS]

    # Find the minimum and maximum x and y coordinates of the lips points
    x_values = [point[0] for point in lips_points]
    y_values = [point[1] for point in lips_points]
    lips_x_min = min(x_values)
    lips_x_max = max(x_values)
    lips_y_min = min(y_values)
    lips_y_max = max(y_values)

    # Increase width and height of the rectangle
    width_increase = 25
    height_increase = 20
    lips_x_min -= width_increase
    lips_x_max += width_increase
    lips_y_min -= height_increase
    lips_y_max += height_increase

    cv.polylines(img,  [np.array([mesh_coords[p] for p in LIPS ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
    cv.rectangle(img, (lips_x_min, lips_y_min), (lips_x_max, lips_y_max), utils.GREEN, 2)
    yeRatio = euclaideanDistance((lips_y_max, lips_y_min), (lips_y_min, lips_y_max))

    re_yawn = yeRatio
    return re_yawn

#=================================================Start========================================================================#
# Variables for counting
blink_right_counter = 0 
blink_left_counter = 0  
blink_right_counter_n = 0 
blink_left_counter_n = 0 
yawn_counter = 0        
blink_right = 0         
blink_left = 0          
re_yawn_counter = 0     
re_yawn_counter_n = 0  
close_eye_right = 0
close_eye_right_counter = 0
close_eye_left = 0
close_eye_left_counter = 0
# variables 
frame_counter = 0
leCEF_COUNTER = 0
leTOTAL_BLINKS = 0
# constants
leCLOSED_EYES_FRAME = 3
reCEF_COUNTER = 0
reTOTAL_BLINKS = 0
# constants
reCLOSED_EYES_FRAME = 3

# Data list for storing results
data = []

Blinks_right_start = 20
Blinks_left_start = 20
Yawn_start = 15

data.append({'Frame': frame_counter, 'Blinks_right': Blinks_right_start, 'Blinks_left': Blinks_left_start, 'Yawns': Yawn_start})
video = cv2.VideoCapture(0)
with map_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    start_time = time.time()
    start_time_right = time.time()
    start_time_left = time.time()
    start_blink_time = time.time()
    start_yawn_time = time.time()
    start_n = time.time()
    frame_count = 0          

    # Starting video loop
    while True:
        frame_counter += 1 # Frame counter
        ret, frame = video.read() # Get frame from camera
        if not ret:
            break # No more frames, break
        n_current_time = time.time()
        n_elapsed_time = n_current_time - start_n
        minutes, seconds = divmod(n_elapsed_time, 60)

        # Resize frame
        frame = cv.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)
        #frame = cropped_frame(frame)
        frame_height, frame_width = frame.shape[:2]
        rgb_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
          mesh_coords = landmarksDetection(frame, results, False)
            # Eye and yawn detection
            #gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            #detectEyes(frame, gray)
          reface = detectFACE(frame, mesh_coords, FACE_OVAL)
          reEYE,leEYE = detecteye(frame, mesh_coords, RIGHT_EYE, LEFT_EYE)
          reYawn = detectYawn(frame, mesh_coords,LIPS)

          if reface > 0 :
                re_face = "face found"
          else:
                re_right = "face NOT found"

          frame = utils.textWithBackground(frame, f'FACE : {re_face}', FONTS, 1.0, (30, 100), bgOpacity=0.9, textThickness=2)
            
          if reface <= 450 :
                frame = utils.textWithBackground(frame, f"Please move your face closer to the camera.", FONTS, 1, (75, 300), bgOpacity=0.9, textThickness=2)
          
          else :
            if reface >= 550 :
                frame = utils.textWithBackground(frame, f"Please move your face go far to the camera.", FONTS, 1, (75, 300), bgOpacity=0.9, textThickness=2)
            if reEYE > 4.7 :
                re_right = "close eye"
                reCEF_COUNTER += 1
            else:
                re_right = "open eye"
                if reCEF_COUNTER > reCLOSED_EYES_FRAME:
                    reTOTAL_BLINKS += 1
                    reCEF_COUNTER = 0

            if leEYE > 4.7 :
                leCEF_COUNTER += 1
                re_left = "close eye"
            else:
                re_left = "open eye"
                if leCEF_COUNTER > leCLOSED_EYES_FRAME:
                    leTOTAL_BLINKS += 1
                    leCEF_COUNTER = 0

            if reYawn > 150 :
                re_yawn = "Yawn"
            else:
                re_yawn = "No Yawn"

            frame = utils.textWithBackground(frame, f'Eye right : {re_right}', FONTS, 1.0, (30, 150), bgOpacity=0.9, textThickness=2)
            frame = utils.textWithBackground(frame, f'Eye left  : {re_left}', FONTS, 1.0, (30, 200), bgOpacity=0.9, textThickness=2)
            frame = utils.textWithBackground(frame, f'Yawn : {re_yawn}', FONTS, 1.0, (30, 250), bgOpacity=0.9, textThickness=2)
            frame = utils.textWithBackground(frame, f'Re Face : {reface}', FONTS, 0.5, (650, 50), bgOpacity=0.45, textThickness=1)
            frame = utils.textWithBackground(frame, f'Re eye right : {reEYE}', FONTS, 0.5, (650, 100), bgOpacity=0.45, textThickness=1)
            frame = utils.textWithBackground(frame, f'Re eye left : {leEYE}', FONTS, 0.5, (650, 150), bgOpacity=0.45, textThickness=1)
            frame = utils.textWithBackground(frame, f'Re Yawn : {reYawn}', FONTS, 0.5, (650, 200), bgOpacity=0.45, textThickness=1)

        # Calculate frame per second (FPS)
        end_time = time.time() - start_time
        fps = (frame_counter / end_time)

        frame = utils.textWithBackground(frame, f'FPS : {round(fps,1)}', FONTS, 1.0, (30, 50), bgOpacity=0.9, textThickness=2)
        #frame = utils.textWithBackground(frame, f'Sound : {Sound}', FONTS, 1.0, (30, 250), bgOpacity=0.9, textThickness=2)
        frame = utils.textWithBackground(frame, "Elapsed Time: {:02d}:{:02d}".format(int(minutes), int(seconds)), FONTS, 0.5, (10, 495), bgOpacity=0.45, textThickness=1)
        frame = utils.textWithBackground(frame, f"Press the 'q' or 'Q' button to close the program", FONTS, 0.5, (10, 525), bgOpacity=0.45, textThickness=1)

        cv.imshow('AI_FallingAsleepDriving',frame)

        key = cv.waitKey(2)
        if key == ord('q') or key == ord('Q') :
            # Store data
            data.append({'Frame': frame_counter, 'Blinks_right': blink_right_counter, 'Blinks_left': blink_left_counter, 'Yawns': re_yawn_counter})
            data.append({
                'Frame': frame_counter,
                'Blinks_right': '{:.2f}%'.format(blink_right_counter / Blinks_right_start * 100),
                'Blinks_left': '{:.2f}%'.format(blink_left_counter / Blinks_left_start * 100),
                'Yawns': '{:.2f}%'.format(re_yawn_counter / Yawn_start * 100)
                })
            # Create a DataFrame from the data list
            df = pd.DataFrame(data)
            df = df.rename(index={0: "Start"})
            df = df.rename(index={1: "Work"})
            df = df.rename(index={2: "Summarize"})

            # Print the DataFrame
            print(df)
            print("-------------------------------------------")
            print("-------close AI_FallingAsleepDriving-------")
            print("-------------------------------------------")
            break

cv.destroyAllWindows()
if start == 1 :
    video.release()