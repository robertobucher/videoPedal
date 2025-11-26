#!/bin/bash

# Start the first application in the 1. terminal
lxterminal -e "sudo ./pedal2Music.py" &

# Start the second application in the 2. terminal
./video2Pedal.py
