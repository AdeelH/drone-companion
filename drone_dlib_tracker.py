import cv2
import dlib
import numpy as np
import ardrone
import math
from statistics import mean
import time
from datetime import datetime
from common import RectSelector
from collections import namedtuple, deque

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
        print('connecting...')
        d = ardrone.ARDrone()
        print('waiting for video...')
        while d.image is None:
            pass

        print('loading calibration info')
        mtx, dist, newcameramtx = getCalibrationInfo()

        out = None

        cv2.imshow('frame', np.array([FRAME_HEIGHT, FRAME_WIDTH, 3]))
        rs = RectSelector('frame', startTracking)

        print('battery remaining:', d.navdata['demo']['battery'])
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
            cv2.imshow('frame', frame)
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
    finally:
        if isFlying:
            land()
        print('halting...')
        d.halt()
        cv2.destroyAllWindows()
        print('battery remaining:', d.navdata['demo']['battery'])
        if isRecording:
            out.release()
        print('bye!')
