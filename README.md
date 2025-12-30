# The application "videoPedal"

## Genesis

This project allows to use a webcam to control a Music application on a tablet (for example MobileSheets) in order to change pages using facial expressions.
MusicSheets contains a similar features, but this is not available on tablet like my BOOX Max Lumi.

The files run in a Raspberry PI 5

## Additional files
The application is wrizzen in Python and exploits the library MEDIAPIPE


```
pip install mediapipe
```

In order to recognize face expressions, the file **face_landmarker_v2_with_blendshapes.task** is required, available at this link. Get this file from Google Face Landmarker Model at

https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/index#models

In addition the btferret git is required to work with bluetooth

```
git clone https://github.com/petzval/btferret.git
python3 btfpymake.py build
```

to obtain the library **btfpy.so**.

At the end of the installation, the folder should contains these files:

```
check_expr.py
createExpr.py
expression.py
face_landmarker_v2_with_blendshapes.task
Makefile
pedal2Music.py
README.md
startMusic.sh
video2Pedal.py
videoParams.ped
btfpy.so
```

To start the application simply move to this folder and run **./startMusic.sh**

At present the application recognize "smile", "mouth open" and "head tilt" (left and right).

It is possible to test the "face" parameters.

Simply open 2 shells.
In the first shell launch
```
./pedal2MusicNoBT.py
```

and in  the second shell launch
```
./video2Pedal.py 1
```

**Attention:** Mediapipe is not yet available for Raspberry with python3.13! It is possible to start it using an environment with python3.11!

This allows to get the openCV frame and tune the face parameters in **videoParams.ped**.

