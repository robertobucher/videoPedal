# The application "videoPedal"

## Genesis

This project allows to use a webcam to control a Music application on a tablet (for example MobileSheets) in order to change pages usin facial expressions.
MusicSheets contains a similar features, but this is not available on tablet like my BOOX Max Lumi.

The files run in a Raspberry PI 5

## Additional files
The application is wrizzen in Python and exploits the library DLIB.


```
pip install dlib
```

In addition the btferret git is required to work with bluetooth

```
git clone https://github.com/petzval/btferret.git
python3 btfpymake.py build
```

to obtain the library **btfpy.so**.

The recognition file **shape_predictor_68_face_landmarks.dat** is available under **https://github.com/davisking/dlib-models.git**

At the end of the installation, the folder should contains these files:

```
btfpy.so
keyboard.txt
pedal2Music.py
shape_predictor_68_face_landmarks.dat
startMusic.sh
video2Pedal.py
videoData.ped
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

This allows to get the openCV frame and tune the face parameters in **videoData.ped**.

