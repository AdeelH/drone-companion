import traceback
import time
import ardrone
from imageProcessor import ImageProcessor
from trackerDlib import Tracker
from locationEstimator import LocationEstimator
from pilot import Pilot
from sensorDataReceiver import SensorDataReceiver
# from guiOpencv import GUI
from guiTk import GUI
from recorder import Recorder
import cv2
import numpy as np
import math


CAM_RES = (640, 360)
displayScalingFactor = 2


class DroneCompanion(object):

	def __init__(self):
		print('Connecting...')
		self.state = {
			'running': True,
			'isFlying': False,
			'isTracking': False,
			'isRecording': False
		}

		self.drone = ardrone.ARDrone()
		self.imageProcessor = ImageProcessor()
		self.pilot = Pilot(self.drone, (0.5, 1, 1, 0.2))
		self.recorder = Recorder((CAM_RES[0] * displayScalingFactor, CAM_RES[1] * displayScalingFactor))
		self.sensorData = None
		self.sensorDataReceiver = SensorDataReceiver(3000, self.receiveSensorData)
		self.sensorDataReceiver.start()
		self.gui = GUI(displayScalingFactor, self.startTracking, self.handleUserInput)

		print('waiting for video...')
		while self.drone.image is None:
			pass
		print('Battery: {0}%'.format(self.drone.navdata['demo']['battery']))

	def receiveSensorData(self, data):
		self.sensorData = data

	def startTracking(self, r):
		x0, y0, x1, y1 = r
		x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
		w, h = x1 - x0, y1 - y0
		self.tracker = Tracker(self.frame, r)
		self.locationEstimator = LocationEstimator(CAM_RES, w, h)
		self.state['isTracking'] = True

	def endTracking(self):
		self.state['isTracking'] = False
		self.gui.undrawRects()

	def track(self, frame):
		rect = self.tracker.update(frame)
		self.gui.drawTrackingRect(rect)
		pos, size = self.locationEstimator.estimate(rect)
		xratio, yratio, xc, yc = pos
		dratio, w, h = size
		if not any([math.isnan(x) for x in [xratio.sum(), yratio.sum(), xc, yc, dratio.sum(), w, h]]):
			x0, y0, x1, y1 = xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2
			self.gui.drawSmoothingRect((x0, y0, x1, y1))
		if self.state['isFlying']:
			self.pilot.follow((xratio, yratio), dratio, self.sensorData)

	def update(self):
		originalFrame = np.array(self.drone.image)
		self.frame = self.imageProcessor.undistort(originalFrame)

		if self.state['isTracking']:
			self.track(self.frame)
		elif self.state['isFlying']:
			if self.drone.navdata['state']['emergency'] == 1:
				self.state['running'] = False
				return
			self.pilot.hover(self.sensorData)

		self.frame = self.imageProcessor.resize(self.frame, displayScalingFactor)
		self.gui.update(self.frame, self.drone.navdata['demo'])
		if self.state['isRecording']:
			self.recorder.record(self.frame)

	def start(self):
		try:
			while self.state['running']:
				self.update()
				self.gui.window.update()
		except Exception:
			traceback.print_exc()
		self.abort()

	def handleUserInput(self, key):
		if key == 'q':
			self.abort()
			self.state['running'] = False
		elif key == ' ':
			if self.state['isFlying']:
				self.pilot.land()
				self.state['isFlying'] = False
			else:
				self.pilot.takeoff()
				self.state['isFlying'] = True
		elif key == 'r':
			if self.state['isRecording']:
				self.recorder.endRecording()
				self.state['isRecording'] = False
			else:
				self.recorder.startNewRecording()
				self.state['isRecording'] = True
		elif key == 'p':
			self.recorder.snap(self.frame)
		elif key == 'c':
			self.endTracking()

	def abort(self):
		self.sensorDataReceiver.stop()
		self.drone.land()
		time.sleep(2)
		self.drone.halt()
		self.gui.handleExit()
		self.sensorDataReceiver.join()
