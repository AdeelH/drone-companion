import cv2
import numpy as np
import ardrone
import time
from datetime import datetime
from common import RectSelector
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
FRAME_WIDTH, FRAME_HEIGHT = 640, 360
CAM_CENTER = Point(int(FRAME_WIDTH / 2), int(FRAME_HEIGHT / 2))

tracker_ind = 0
trackers = ['TLD', 'KCF', 'MIL', 'MEDIANFLOW', 'BOOSTING']

cv2.ocl.setUseOpenCL(False)
tracker = None
isTracking = False
isRecording = False
found = False
roi = None


def start_tracking(r):
    global tracker
    global isTracking
    x0, y0, x1, y1 = r
    w, h = (x1 - x0), (y1 - y0)
    tracker = cv2.Tracker_create(trackers[tracker_ind])
    isTracking = tracker.init(frame, (x0, y0, w, h))


def follow(d, x, y):
    dx, dy = x - CAM_CENTER.x, CAM_CENTER.y - y
    dx_scaled, dy_scaled = (dx / CAM_CENTER.x), (dy / CAM_CENTER.y)
    d.move(0, 0, dy_scaled, dx_scaled)


def getCalibrationInfo():
    mtx = np.loadtxt('calibration/mtx')
    dist = np.loadtxt('calibration/dist')
    newcameramtx = np.loadtxt('calibration/newcameramtx')
    return mtx, dist, newcameramtx


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
        rs = RectSelector('frame', start_tracking)

        # print('3 ... 2 ... 1 ...')
        # print('battery remaining:', d.navdata['demo']['battery'])
        # d.trim()
        # d.takeoff()
        # print('lift off!')

        while True:
            frame = cv2.cvtColor(np.array(d.image), cv2.COLOR_RGB2BGR)
            # frame = cv2.undistort(frame, mtx, dist)
            frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)
            if rs.dragging:
                rs.draw(frame)
            if isTracking:
                found, rect = tracker.update(frame)
                if found:
                    x, y, w, h = rect
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    xc, yc = int(x + (w / 2)), int(y + (h / 2))
                    follow(d, xc, yc)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255))
                    cv2.circle(frame, CAM_CENTER, 5, (0, 0, 255), thickness=4)
                    cv2.line(frame, (xc, yc), (CAM_CENTER.x, CAM_CENTER.y), (0, 255, 0))
                else:
                    d.hover()
            else:
                d.hover()

            if isRecording:
                out.write(frame)

            cv2.imshow('frame', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('r'):
                print('r')
                isRecording = not isRecording
            elif k == ord('t'):
                tracker_ind = (tracker_ind + 1) % len(trackers)
                print('tacker', trackers[tracker_ind])
    finally:
        print('landing...')
        d.land()
        time.sleep(2)
        print('battery remaining:', d.navdata['demo']['battery'])
        print('halting...')
        d.halt()
        print('press any key to exit')
        k = cv2.waitKey()
        cv2.destroyAllWindows()
        out.release()
        print('bye!')
