import dlib


class Tracker(object):

	def __init__(self, frame, rect):
		self.tracker = dlib.correlation_tracker()
		x0, y0, x1, y1 = rect
		x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
		self.tracker.start_track(frame, dlib.rectangle(x0, y0, x1, y1))

	def update(self, frame):
		self.tracker.update(frame)
		r = self.tracker.get_position()
		x0, y0, x1, y1 = r.left(), r.top(), r.right(), r.bottom()
		x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
		return (x0, y0, x1, y1)
