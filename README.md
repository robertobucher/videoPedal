# The application "videoPedal"

## Genesis

This project allows to use a webcam to control a Music application on a tablet (for example MobileSheetsPro) in order to change pages usin facial expressions.
MusicSheetsPro contains a similar features, but this is not available on tablet like Boxx Max Lumi.

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



