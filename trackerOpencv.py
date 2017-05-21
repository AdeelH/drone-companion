import cv2


class TrackerOpencv(object):

	def __init__(self, tname, frame, rect):
		self.tracker = cv2.Tracker_create('TLD')
		x0, y0, x1, y1 = rect
		x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
		w, h = x1 - x0, y1 - y0
		self.tracker.init(frame, (x0, y0, w, h))

	def update(self, frame):
		found, rect = self.tracker.update(frame)
		x0, y0, w, h = rect
		x0, y0, w, h = int(x0), int(y0), int(w), int(h)
		return (x0, y0, x0 + w, y0 + h)
