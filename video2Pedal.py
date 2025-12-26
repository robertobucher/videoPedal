#!/usr/bin/python3

import cv2
import numpy as np
import time
import socket
import os
import json
import sys

from expression import *

if MP:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
else:
    import dlib

DBG = True
SOCK = True
NEUTRAL = 0

if len(sys.argv) < 2:
    DBG = False

# Debug Mode for local test (comment for real app!))
# DBG = True
# SOCK = False

if MP:
    outFile = 'videoParams.ped'
    L_MOUTH = 61      # Left mouth angle
    R_MOUTH = 291     # Right mouth anle
    TOP_LIP = 13      # Center mouth up (inner)
    BOTTOM_LIP = 14      # Center mouth bottom (inner)
    L_FACE = 234      # Face left
    R_FACE = 454      # Face right
    NOSE = 4            # Nose
else:              #dlib
    outFile = 'videoData.ped'
    L_MOUTH = 48      # Left mouth angle
    R_MOUTH = 54     # Right mouth anle
    TOP_LIP = 62      # Center mouth up (inner)
    BOTTOM_LIP = 66      # Center mouth bottom (inner)
    L_FACE = 0      # Face left
    R_FACE = 16      # Face right
    NOSE = 30          # Nose

if MP:
    # INIT MEDIAPIPE TASKS
    model_path = 'face_landmarker_v2_with_blendshapes.task'

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)
    # Load parameters
    with open('videoParams.ped', 'r') as f:
        params = json.load(f)
else:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    # Load parameters
    with open('videoData.ped', 'r') as f:
        params = json.load(f)

INHIBITION_TIME = params['FREEZE_TIME']

EVENTS = []

par = params['NEUTRAL']
EVENTS.append(Expression(NEUTRAL, par))

# Choice of active events
par = params['MOUTH_OPEN']
EVENTS.append(mouthOpenExpr(1, par))
par = params['KISS']
EVENTS.append(kissExpr(2,par))

# States and events initialization
prev_status = NEUTRAL
act_status = NEUTRAL
status_start_time = time.time()
action_sent = False
last_action_time = 0.0

# Unix Socket Client
def set_client():
    socket_path = '/tmp/my_socket'
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    return client

def shape_to_np(shape):
    """Convert landmarks of Dlib into a NumPy array (x, y)."""
    coords = np.zeros((68, 2), dtype=int)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def capture_state(ev, LM):
    for el in ev:
        if el.check(LM):
            return el.state
    return NEUTRAL

def update_state(current_status, ev):
    global prev_status, status_start_time, action_sent

    if current_status != prev_status:
        prev_status = current_status
        status_start_time = time.time()
        action_sent = False
        return current_status, False

    elapsed = time.time() - status_start_time
    reftime = ev[current_status].waitTime

    if elapsed >= reftime:
        if not action_sent:
            action_sent = True
            return current_status, True
    return current_status, False

# Open socket
if SOCK:
    pedalApp = set_client()

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Camera not ok")
    exit()

while True:
    ret, frame = cap.read()
    if not ret: break
    landmarks = []

    if MP:
        # Conversion for MediaPipe Tasks
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Get landmarks
        result = detector.detect(mp_image)

        if result.face_landmarks:
            # Landmarks for 1. face
            landmarks = result.face_landmarks[0]
            ok = True
    else:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 0) # 0 allows more speed     # Use this instead for only DLIB
        face = faces[0]

        (x1, y1, x2, y2) = (face.left(), face.top(), face.right(), face.bottom())

        # Face (disegna il rettangolo usando le coordinate Haar/dlib)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Get the 68 landmarks (il predictor dlib è ancora necessario!)
        shape = predictor(gray, face)
        landmarks = shape_to_np(shape)
        ok = True

    if ok:
        # Get states
        status_text = ''
        act_status = capture_state(EVENTS, landmarks)
        act_status, actionFlag = update_state(act_status, EVENTS)

        # Send action to pedal App
        current_time = time.time()
        is_cooldown_active = current_time < last_action_time + INHIBITION_TIME

        if actionFlag and not is_cooldown_active:
            keyS = EVENTS[act_status].command
            if keyS != '0':
                print('Sending ' + EVENTS[act_status].text)
                if SOCK:
                    pedalApp.sendall(keyS.encode())
                last_action_time = current_time

        if is_cooldown_active:
            status_text = 'WAIT ' + EVENTS[act_status].text
        elif actionFlag:
            status_text = EVENTS[act_status].text

        # Draw Landmark for Debug
        if DBG:
            if MP:
                h, w, _ = frame.shape
                # Draw only the selected landmarks
                for idx in [L_MOUTH, R_MOUTH, TOP_LIP, BOTTOM_LIP, L_FACE, R_FACE, NOSE]:
                    pt = landmarks[idx]
                    cv2.circle(frame, (int(pt.x * w), int(pt.y * h)), 2, (0, 255, 0), -1)
            else:
                # Plot landmarks
                for (x, y) in landmarks:
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Face Expression', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
if SOCK:
    pedalApp.close()
