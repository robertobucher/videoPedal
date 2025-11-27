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

DPAD_UP = '30'
DPAD_DOWN = '31'

MAR = 0.30                                 # MOUTH OPEN
MOUTH_RATIO = 0.35                # SMILE
HEAD_TILT_THRESHOLD = 30    # pixel di differenza tra mandibole

FIX_TIME = 0.8

prev_status = NEUTRAL
act_status = NEUTRAL
status_start_time = time.time()
action_sent = False
actionFlag = False

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# ---------- SMILE and MOUTH OPEN----------
def calculate_mouth_ratio(landmarks):
    """Calculate Mouth Aspect Ratio - MAR)."""

    # Mouth width 60 e 64)
    A = np.linalg.norm(landmarks[60] - landmarks[64])

    # Mouth height62 e 66)
    B = np.linalg.norm(landmarks[62] - landmarks[66])

    # return Height/Width (B/A)
    return B / A, A

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

    # Se lo stato cambia → reset timer e flag
    if current_status != prev_status:
        prev_status = current_status
        status_start_time = time.time()
        action_sent = False
        return current_status, False

    # Se è lo stesso stato, controlla il tempo
    elapsed = time.time() - status_start_time

    if elapsed >= FIX_TIME:
        # Se il tempo è passato ma non abbiamo ancora inviato l'azione
        if not action_sent:
            action_sent = True
            return current_status, True  # possiamo inviare
        else:
            return current_status, False  # già inviato, non ripetere

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
    elif mouth_width > (face_width * MOUTH_RATIO):
        return SMILE
    elif tilt > HEAD_TILT_THRESHOLD:
        return HEAD_TILT_LEFT
    elif tilt < -HEAD_TILT_THRESHOLD:
        return HEAD_TILT_RIGHT       
    else:
        return NEUTRAL

def check_time(t, reftime):
    if time.time()-t >= reftime:
        return True
    else:
        return False

def get_face_state(act_st):
    global prev_time, old_status
    if act_st != old_status:
        prev_time = time.time()
        prev_status = act_st
        ok = False
    else:
        if check_time(prev_time, REFTIME[act_st]):
            ok = True
        else:
            ok = False

    return act_st, ok

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
FIX_TIME = params['FIXTIME']
TIME_SMILE = params['TIME_SMILE']
TIME_MOUTH = params['TIME_MOUTH']

# NEUTRAL = 0
# MOUTH_OPEN = 1
# SMILE = 2
# HEAD_TILT_LEFT = 3
# HEAD_TILT_RIGHT = 4

REFTIME = [FIX_TIME, TIME_MOUTH, TIME_SMILE, FIX_TIME, FIX_TIME]

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

    TXT_STATUS = ['NEUTRAL', 'MOUTH OPEN', 'SMILE', 'HEAD_TILT_LEFT', 'HEAD_TILT_RIGHt']
    TXT_KEY = ['0', DPAD_DOWN, DPAD_UP, DPAD_UP, DPAD_DOWN]

    if actionFlag:
        print("Sending:", TXT_STATUS[act_status])
        status_text = TXT_STATUS[act_status]
        keyS = TXT_KEY[act_status]
        if keyS != '0':
            pedalApp.sendall(keyS.encode())
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

