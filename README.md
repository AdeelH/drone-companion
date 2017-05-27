# AR Drone Companion
A desktop app for the Parrot AR Drone 2.0. Specify a target in the video and watch the AR Drone autonomously track and follow it. The drone also avoids obstacles using data from mounted ultrasonic sensors. (Final Year Project, Fall 2016 - Spring 2017)

## Run
`python app.py`

## Controls
`<space>` - takeoff/land  
`r` - start/stop recording  
`p` - take a picture  
`c` - stop tracking  
`q` - quit  

## Dependencies
- [python-ardrone](https://github.com/AdeelH/python-ardrone)
- OpenCV
- Dlib
- NumPy
