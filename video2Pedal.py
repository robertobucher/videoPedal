#!/usr/bin/python3

import cv2
import dlib
import numpy as np
import time
import socket
import os
import json
import sys

DBG = True

if len(sys.argv) < 2:
    DBG = False

NEUTRAL = 0
MOUTH_OPEN = 1
SMILE = 2
HEAD_TILT_LEFT = 3
HEAD_TILT_RIGHT = 4
KISS = 5

DPAD_UP = '30'
DPAD_DOWN = '31'

MAR = 0.30                                 # MOUTH OPEN
MOUTH_RATIO = 0.35                # SMILE
HEAD_TILT_THRESHOLD = 30    # pixel di differenza tra mandibole
KISS_RATIO = 0.15

FIX_TIME = 0.8
INHIBITION_TIME = 2.0
TXT_KEY = ['0', DPAD_DOWN, DPAD_UP, DPAD_DOWN, DPAD_UP,  DPAD_DOWN]

prev_status = NEUTRAL
act_status = NEUTRAL
status_start_time = time.time()
action_sent = False
actionFlag = False
last_action_time = 0.0

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# ---------- SMILE and MOUTH OPEN----------
def calculate_mouth_ratio(landmarks):
    """Calculate Mouth Aspect Ratio (MAR) e la larghezza esterna della bocca (W_ext)."""

    # Mouth width (prev 60 - 64)
    # W_ext = np.linalg.norm(landmarks[48] - landmarks[54])
    W_ext = np.linalg.norm(landmarks[60] - landmarks[64])

    # Mouth height 
    H_int = np.linalg.norm(landmarks[62] - landmarks[66])

    # MAR = Altezza/Larghezza (H_int / W_ext)
    mar = H_int / W_ext

    return mar, W_ext # Restituiamo W_ext che è la larghezza ora

# ---------- HEAD TILT ----------
def head_tilt_value(landmarks):
    jaw_left_y = landmarks[1][1]
    jaw_right_y = landmarks[15][1]
    return jaw_left_y - jaw_right_y  # positivo → inclinato verso sinistra

def update_state(current_status):
    """
    Ritorna (status, ready) dove:
      - status = stato corrente
      - ready = True se lo stato è stabile da FIX_TIME secondi
    """
    global prev_status, status_start_time, action_sent

    # If state change → reset timer e flag
    if current_status != prev_status:
        prev_status = current_status
        status_start_time = time.time()
        action_sent = False
        return current_status, False

    # If same state → check time
    elapsed = time.time() - status_start_time

    if current_status >= 0 and current_status < len(REFTIME):
        reftime = REFTIME[current_status]
    else:
        reftime = FIX_TIME 

    if elapsed >= reftime:
        if not action_sent:
            action_sent = True
            return current_status, True  
        else:
            return current_status, False  

    return current_status, False

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

def capture_state(mar, mouth_width, face_width, tilt):
    if mar > MAR:
        return MOUTH_OPEN
    elif mouth_width < (face_width * KISS_RATIO): 
        return KISS 
    elif mouth_width > (face_width * MOUTH_RATIO):
        return SMILE
    elif tilt > HEAD_TILT_THRESHOLD:
        return HEAD_TILT_RIGHT
    elif tilt < -HEAD_TILT_THRESHOLD:
        return HEAD_TILT_LEFT
    else:
        return NEUTRAL

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
state = 0

if not cap.isOpened():
    print("Camera not ok")
    exit()

f = open('videoData.ped', 'r')
msg = f.read()
f.close()
params = json.loads(msg)
MAR =  params['MOUTH']                      # MOUTH OPEN
MOUTH_RATIO = params['SMILE']         # SMILE
HEAD_TILT_THRESHOLD =  params['TILT']
KISS_RATIO = params['KISS']

FIX_TIME = params['FIXTIME']
TIME_SMILE = params['TIME_SMILE']
TIME_MOUTH = params['TIME_MOUTH']
TIME_TILT = params['TIME_TILT']
TIME_KISS = params['TIME_KISS']
INHIBITION_TIME = params['FREEZE_TIME']

# 30 = NEXT PAGE
# 31 = PREV PAGE
TXT_KEY = params['ACTIONS']

# NEUTRAL = 0
# MOUTH_OPEN = 1
# SMILE = 2
# HEAD_TILT_LEFT = 3
# HEAD_TILT_RIGHT = 4

REFTIME = [FIX_TIME, TIME_MOUTH, TIME_SMILE, TIME_TILT, TIME_TILT, TIME_KISS]

pedalApp = set_client()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray, 0) # 0 allows more speed     # Use this instead for only DLIB

    for face in faces:
        (x1, y1, x2, y2) = (face.left(), face.top(), face.right(), face.bottom())

        # Face (disegna il rettangolo usando le coordinate Haar/dlib)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Get the 68 landmarks (il predictor dlib è ancora necessario!)
        shape = predictor(gray, face)
        landmarks = shape_to_np(shape)

        # Mouth metrix
        mar, mouth_width = calculate_mouth_ratio(landmarks)

        # Face
        face_width = np.linalg.norm(landmarks[0] - landmarks[16])

        # Head tilt
        tilt = head_tilt_value(landmarks)

        # Check Face gesture
        act_status = capture_state(mar, mouth_width, face_width, tilt)
        act_status, actionFlag = update_state(act_status)

        # Plot landmarks
        for (x, y) in landmarks:
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    TXT_STATUS = ['NEUTRAL', 'MOUTH OPEN', 'SMILE',
                  'HEAD_TILT_LEFT', 'HEAD_TILT_RIGHT', 'KISS']
    
    # DPAD_UP = '30'
    # DPAD_DOWN = '31'
    # TXT_KEY = ['0', DPAD_DOWN, DPAD_UP, DPAD_DOWN, DPAD_UP]

    current_time = time.time()
    is_cooldown_active = current_time < last_action_time + INHIBITION_TIME

    if actionFlag and not is_cooldown_active:
        status_text = TXT_STATUS[act_status]
        keyS = TXT_KEY[act_status]

        if keyS != '0':
            print("Sending:", TXT_STATUS[act_status])
            pedalApp.sendall(keyS.encode())
            last_action_time = current_time # Aggiorna il timestamp dell'ultima azione

    if actionFlag and not is_cooldown_active:
        status_text = TXT_STATUS[act_status]
    else:
        status_text = ''

    if DBG:
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Face Expression Recognition (Dlib)', frame)

    # Exit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

pedalApp.close()

