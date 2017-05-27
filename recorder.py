import cv2
from datetime import datetime


class Recorder(object):

	def __init__(self, camRes):
		self.codec = cv2.VideoWriter_fourcc(*'XVID')
		self.camRes = camRes

	def startNewRecording(self):
		timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
		self.out = cv2.VideoWriter('recordings/{0}.avi'.format(timestamp), self.codec, 30.0, self.camRes)

	def record(self, frame):
		self.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

	def snap(self, frame):
		timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
		cv2.imwrite('snapshots/{0}.jpg'.format(timestamp), frame)

	def endRecording(self):
		self.out.release()
