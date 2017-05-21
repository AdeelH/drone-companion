import numpy as np
from particleFilter import ParticleFilter


class LocationEstimator(object):

	def __init__(self, camRes, w, h):
		camWidth, camHeight = camRes
		self.maxWidth, self.maxHeight = camWidth / 2, camHeight / 2
		self.posParticles = ParticleFilter(200, camWidth, camHeight, 20, 10, 0.1)
		self.sizeParticles = ParticleFilter(200, camWidth, camHeight, 20, 10, 0.1)
		self.initialSize = (w, h)

	def estimate(self, rect):
		x0, y0, x1, y1 = rect
		xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
		w, h = x1 - x0, y1 - y0
		return self.estimatePos(xc, yc), self.estimateSize(w, h)

	def estimatePos(self, xc, yc):
		self.posParticles.update(np.array([xc, yc]))
		x, y = self.posParticles.consensus()
		dx, dy = x - self.maxWidth, self.maxHeight - y
		dxRatio, dyRatio = dx / self.maxWidth, dy / self.maxHeight
		return dxRatio, dyRatio, x, y

	def estimateSize(self, w, h):
		self.sizeParticles.update(np.array([w, h]))
		w, h = self.sizeParticles.consensus()
		if w > h:
			distRatio = self.initialSize[0] / w
		else:
			distRatio = self.initialSize[1] / h
		return distRatio, w, h
