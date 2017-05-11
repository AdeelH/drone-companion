import cv2
import dlib
import numpy as np
import ardrone
from statistics import mean
import time
from datetime import datetime
from common import RectSelector
from collections import namedtuple, deque
from piData import PiThread
import math
import tkinter
from tkinter import *
from PIL import ImageTk, Image

Point = namedtuple('Point', ['x', 'y'])
Size = namedtuple('Size', ['w', 'h'])
FRAME_WIDTH, FRAME_HEIGHT = 640, 360
CAM_CENTER = Point(int(FRAME_WIDTH / 2), int(FRAME_HEIGHT / 2))
isFlying = False

trackerInd = 0
trackers = ['TLD', 'KCF', 'MIL', 'MEDIANFLOW', 'BOOSTING']

cv2.ocl.setUseOpenCL(False)
tracker = None
isTracking = False
isRecording = False
found = False
tracker = dlib.correlation_tracker()
initialArea = None
initialSize = None
sizeHistory = deque([], 10)
MIN_HEIGHT = 100
MAX_FORWARD_V = 1

piData = ''
battery_images = [Image.open("0.png"), Image.open("25.png"), Image.open("50.png"), Image.open("75.png"), Image.open("100.png")]


def updateStream(tmp):
    global img_bg
    img_bg = tmp
    canvas.itemconfigure(droneImage, image=img_bg)
    return


def updateBattery(battery):  # Check if changed
    canvas.itemconfigure(batteryPercent, text=str(battery)+"%")

    global img_battery
    tmp = battery_images[int(math.ceil(battery/25))]
    img_battery = ImageTk.PhotoImage(tmp.resize((int(tmp.width / 7), int(tmp.height / 7))))
    canvas.itemconfigure(batteryIcon, image=img_battery)
    return


def recordPressed(event):
    global recImg
    if (1200 < event.x < 1200+recImg.width()) and (650 < event.y < 650+recImg.height()):
        print("recording dat shit")
    return
###############################################################


def getPiData(d):
    global s
    s = d
    print(s)


def startTracking(r):
    global tracker
    global initialArea
    global initialSize
    global isTracking
    x0, y0, x1, y1 = r
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    tracker.start_track(frame, dlib.rectangle(x0, y0, x1, y1))
    w, h = x1 - x0, y1 - y0
    initialArea = w * h
    initialSize = Size(w, h)
    isTracking = True


def follow(d, x0, x1, y0, y1):
    w, h = x1 - x0, y1 - y0
    x, y = int(x0 + (w / 2)), int(y0 + (h / 2))
    dx, dy = x - CAM_CENTER.x, CAM_CENTER.y - y
    angularV, verticalV = (dx / CAM_CENTER.x), (dy / CAM_CENTER.y)**2

    sizeHistory.append((w, h))
    if w > h:
        wSmoothed = mean([w for w, h in sizeHistory])
        sizeRatio = initialSize.w / wSmoothed
    else:
        hSmoothed = mean([h for w, h in sizeHistory])
        sizeRatio = initialSize.h / hSmoothed
    # if too close
    if sizeRatio < 1:
        # move backward = positive forward tilt
        forwardTilt = min(1 - sizeRatio, MAX_FORWARD_V)
    else:
        # move forward = negative forward tilt
        forwardTilt = max(-min((sizeRatio - 1), 1), -MAX_FORWARD_V)
    forwardTilt = forwardTilt**2 if forwardTilt > 0 else -(forwardTilt**2)
    print("forwardTilt", forwardTilt)
    altitude = d.navdata['demo']['altitude']
    # print('theta', d.navdata['demo']['theta'], 'phi', d.navdata['demo']['phi'], 'psi', d.navdata['demo']['psi'])

    if altitude <= MIN_HEIGHT and verticalV < 0:
        print('must ... not ... touch ... ground')
        verticalV = 0
    m = max(abs(forwardTilt), abs(verticalV), abs(angularV))
    if m < 0.05:
        d.hover()
    else:
        d.move(0, forwardTilt, verticalV, angularV)


def getCalibrationInfo():
    mtx = np.loadtxt('calibration/mtx')
    dist = np.loadtxt('calibration/dist')
    newcameramtx = np.loadtxt('calibration/newcameramtx')
    return mtx, dist, newcameramtx


def land():
    print('landing...')
    d.land()
    time.sleep(2)


if __name__ == '__main__':
    try:
        window = Tk()
        window.wm_title("Sparrow")
        frame = Frame(window, width=1280, height=720).grid(row=0, column=0, rowspan=3, columnspan=40)
        canvas = tkinter.Canvas(frame, width=1280, height=720)
        canvas.grid(row=0, column=0, rowspan=3, columnspan=40)

        droneImage = canvas.create_image(0, 0, anchor=NW)

        batteryIcon = canvas.create_image(12, 650, anchor=NW)
        batteryPercent = canvas.create_text(70, 682, font=("Bold", 18), fill='white')

        recImg = Image.open("record.png")
        recImg = ImageTk.PhotoImage(recImg.resize((int(recImg.width / 9), int(recImg.height / 9))))
        canvas.create_image(1200, 650, image=recImg, anchor=NW)
        canvas.bind("<Button-1>", recordPressed)

        updateStream(ImageTk.PhotoImage(Image.open("emptyroad.jpg")))  # drone.image.show()
        updateBattery(76)  # drone.navdata['demo']['battery']

########################################################################################################################

        print('Starting server for Pi')
        piThread = PiThread(getPiData)
        piThread.start()

        print('connecting...')
        d = ardrone.ARDrone()
        print('waiting for video...')
        while d.image is None:
            pass

        print('loading calibration info')
        mtx, dist, newcameramtx = getCalibrationInfo()

        out = None

        # cv2.imshow('frame', np.array([FRAME_HEIGHT, FRAME_WIDTH, 3]))    #######Changed
        rs = RectSelector('frame', startTracking)

        print('battery remaining:', d.navdata['demo']['battery'])
        updateBattery(d.navdata['demo']['battery'])
        if d.navdata['state']['emergency'] == 1:
            d.reset()

        while True:
            frame = cv2.cvtColor(np.array(d.image), cv2.COLOR_RGB2BGR)
            # frame = cv2.undistort(frame, mtx, dist)
            frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)
            if rs.dragging:
                rs.draw(frame)
            if isTracking:
                tracker.update(frame)
                r = tracker.get_position()
                x0, y0 = int(r.left()), int(r.top())
                x1, y1 = int(r.right()), int(r.bottom())
                follow(d, x0, x1, y0, y1)
                cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 0, 255))
                # cv2.line(frame, (xc, yc), (CAM_CENTER.x, CAM_CENTER.y), (0, 255, 0))

            if isRecording:
                out.write(frame)

            cv2.circle(frame, CAM_CENTER, 1, (0, 0, 255), thickness=4)
            # cv2.imshow('frame', frame)    #####Changed
            updateStream(frame)
            k = chr(cv2.waitKey(1) & 0xFF)
            if k == 'q':
                break
            elif k == 'r':
                print('recording')
                if out is None:
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                    out = cv2.VideoWriter('recordings/{0}.avi'.format(timestamp), fourcc, 30.0, (640, 360))
                    isRecording = True
                else:
                    out.release()
                    isRecording = False
            elif k == 'c':
                isTracking = False
            elif k == ' ':
                if isFlying:
                    land()
                    isFlying = False
                else:
                    print('3 ... 2 ... 1 ...')
                    d.trim()
                    d.takeoff()
                    print('lift off!')
                    isFlying = True
            elif k == 'z':
                d.turn_left()
            elif k == 'x':
                d.turn_right()
            elif k == 'a':
                d.move_left()
            elif k == 'd':
                d.move_right()
            elif k == 'w':
                d.move_forward()
            elif k == 's':
                d.move_backward()
            else:
                d.hover()
            window.update()
    finally:
        if isFlying:
            land()
        print('halting...')
        d.halt()
        cv2.destroyAllWindows()
        print('battery remaining:', d.navdata['demo']['battery'])
        updateBattery(d.navdata['demo']['battery'])
        if isRecording:
            out.release()
        print('bye!')
