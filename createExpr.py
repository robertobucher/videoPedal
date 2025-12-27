import json

MP = True       # Mediapipe available
# Commands   30: prev page  31: next page

if MP:
    outFile = 'videoParams.ped'
    L_MOUTH = 61      # Left mouth angle
    R_MOUTH = 291     # Right mouth anle
    TOP_LIP = 13      # Center mouth up (inner)
    BOTTOM_LIP = 14      # Center mouth bottom (inner)
    L_FACE = 234      # Face left
    R_FACE = 454      # Face right
    NOSE = 4            # Nose
    L_PUFF = 123      # Left puff
    R_PUFF = 352      # Right puff
else:              #dlib
    outFile = 'videoData.ped'
    L_MOUTH = 48      # Left mouth angle
    R_MOUTH = 54     # Right mouth anle
    TOP_LIP = 62      # Center mouth up (inner)
    BOTTOM_LIP = 66      # Center mouth bottom (inner)
    L_FACE = 0      # Face left
    R_FACE = 16      # Face right
    NOSE = 30          # Nose
    L_PUFF = 123      # Left puff
    R_PUFF = 352      # Right puff

neutral = {
    'TEXT' : 'NEUTRAL',
    'COMMAND' : 0,
    'COND' : 0,
    'WAIT' : 0.4,
    'LANDMARK' : []
}

smile = {
    'TEXT' : 'SMILE',
    'COMMAND' : 30,
    'COND' : 0.25,
    'WAIT' : 0.4,
    'LANDMARK' : [L_MOUTH, R_MOUTH, L_FACE, R_FACE]
}

kiss = {
    'TEXT' : 'KISS',
    'COMMAND' : 30,
    'COND' : 0.30,
    'WAIT' : 0.4,
    'LANDMARK' : [L_MOUTH, R_MOUTH, L_FACE, R_FACE]
}

mouthOpen = {
    'TEXT' : 'MOUTH OPEN',
    'COMMAND' : 30,
    'COND' : 0.2,
    'WAIT' : 0.4,
    'LANDMARK' : [L_MOUTH, R_MOUTH, TOP_LIP, BOTTOM_LIP]
}

tiltRight = {
    'TEXT' : 'TILT RIGHT',
    'COMMAND' : 30,
    'COND' : 20,
    'WAIT' : 0.4,
    'LANDMARK' : [L_FACE, R_FACE]
}

tiltLeft = {
    'TEXT' : 'TILT LEFT',
    'COMMAND' : 30,
    'COND' : 20,
    'WAIT' : 0.4,
    'LANDMARK' : [L_FACE, R_FACE]
}

tongueRight = {
    'TEXT' : 'TONGUE RIGHT',
    'COMMAND' : 30,
    'COND' : 0.02,
    'WAIT' : 0.4,
    'LANDMARK' : [NOSE, TOP_LIP, BOTTOM_LIP]
}

tongueLeft = {
    'TEXT' : 'TONGUE LEFT',
    'COMMAND' : 30,
    'COND' : 0.02,
    'WAIT' : 0.4,
    'LANDMARK' : [NOSE, TOP_LIP, BOTTOM_LIP]
}

puffLeft = {
    'TEXT' : 'PUFF LEFT',
    'COMMAND' : 31,
    'COND' : 0.15,
    'WAIT' : 0.4,
    'LANDMARK' : [NOSE, L_PUFF]
}

puffRight = {
    'TEXT' : 'PUFF RIGHT',
    'COMMAND' : 30,
    'COND' : 0.15,
    'WAIT' : 0.4,
    'LANDMARK' : [NOSE, R_PUFF]
}


ACTIONS = {
    'FREEZE_TIME' : 1.0,
    'NEUTRAL' : neutral,
    'SMILE' : smile,
    'KISS' : kiss,
    'MOUTH_OPEN' : mouthOpen,
    'TILT_RIGHT' : tiltRight,
    'TILT_LEFT' : tiltLeft,
    'TONGUE_RIGHT' : tongueRight,
    'TONGUE_LEFT' : tongueLeft,
    'PUFF_LEFT' : puffLeft,
    'PUFF_RIGHT' : puffRight
}

msg = json.dumps(ACTIONS)
f = open(outFile, 'w')
f.write(msg)
f.close()



