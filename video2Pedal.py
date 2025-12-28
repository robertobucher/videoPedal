#!/usr/bin/python3

import cv2
import numpy as np
import time
import socket
import json
import sys

from expression import *

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

DBG = True
SOCK = True
NEUTRAL = 0

if len(sys.argv) < 2:
    DBG = False

# Debug Mode for local test (comment for real app!))
DBG = True
SOCK = False

outFile = 'videoParams.ped'
L_MOUTH = 61      # Left mouth angle
R_MOUTH = 291     # Right mouth anle
TOP_LIP = 13      # Center mouth up (inner)
BOTTOM_LIP = 14      # Center mouth bottom (inner)
L_FACE = 234      # Face left
R_FACE = 454      # Face right
L_PUFF = 123      # Left puff
R_PUFF = 352      # Right puff
NOSE = 4            # Nose

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

INHIBITION_TIME = params['FREEZE_TIME']
EXPRESSIONS = params['EXPRESSIONS']

EVENTS = []

for el in EXPRESSIONS:
    par = params[el]
    cls = classes[el]
    EVENTS.append(cls(EXPRESSIONS.index(el), par))

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

    # Conversion for MediaPipe Tasks
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Get landmarks
    result = detector.detect(mp_image)

    if result.face_landmarks:
        # Landmarks for 1. face
        landmarks = result.face_landmarks[0]

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
            h, w, _ = frame.shape
            # Draw only the selected landmarks
            for idx in [L_MOUTH, R_MOUTH, TOP_LIP, BOTTOM_LIP, L_FACE, R_FACE, NOSE, L_PUFF, R_PUFF]:
                pt = landmarks[idx]
                cv2.circle(frame, (int(pt.x * w), int(pt.y * h)), 2, (0, 255, 0), -1)

            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Face Expression', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
if SOCK:
    pedalApp.close()
