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
areaHistory = deque([], 10)


def startTracking(r):
    global tracker
    global initialArea
    global isTracking
    x0, y0, x1, y1 = r
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    tracker.start_track(frame, dlib.rectangle(x0, y0, x1, y1))
    w, h = x1 - x0, y1 - y0
    initialArea = w * h
    isTracking = True


def follow(d, x0, x1, y0, y1):
    w, h = x1 - x0, y1 - y0
    x, y = int(x0 + (w / 2)), int(y0 + (h / 2))
    dx, dy = x - CAM_CENTER.x, CAM_CENTER.y - y
    va, vv = (dx / CAM_CENTER.x), (dy / CAM_CENTER.y)

    areaHistory.append(w * h)
    area = mean(areaHistory)
    fb = (1 - (initialArea / area)**2)
    fb = min(0.1, max(-0.1, fb))
    print(d.navdata['demo']['altitude'])
    if d.navdata['demo']['altitude'] < 250 and vv < 0:
        vv = 0
    d.move(0, fb, vv, va)


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

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        out = cv2.VideoWriter('recordings/{0}.avi'.format(timestamp), fourcc, 30.0, (640, 360))

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
            else:
                d.hover()

            if isRecording:
                out.write(frame)

            cv2.circle(frame, CAM_CENTER, 1, (0, 0, 255), thickness=4)
            cv2.imshow('frame', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('r'):
                print('r')
                isRecording = not isRecording
            elif k == ord('t'):
                trackerInd = (trackerInd + 1) % len(trackers)
                print('tacker', trackers[trackerInd])
            elif k == ord('c'):
                isTracking = False
            elif k == ord(' '):
                if isFlying:
                    land()
                    isFlying = False
                else:
                    print('3 ... 2 ... 1 ...')
                    d.trim()
                    d.takeoff()
                    print('lift off!')
                    isFlying = True
    finally:
        if isFlying:
            land()
        print('battery remaining:', d.navdata['demo']['battery'])
        print('halting...')
        d.halt()
        cv2.destroyAllWindows()
        out.release()
        print('bye!')
