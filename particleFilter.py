import numpy as np
from scipy.stats import multivariate_normal as mvn


class ParticleFilter(object):

	def __init__(self, n, x, y, sensorVar, diffMag, noisyRatio=0.1):
		self.n = n
		self.nn = int(n * noisyRatio)
		self.x = x
		self.y = y
		self.particles = self.genParticles(self.n, x, y)
		self.sensorVar = np.eye(2) * sensorVar
		self.diffusionMagnitude = diffMag
		self.ws = np.ones((n, 1))[:, 0] / n

	def genParticles(self, n, x, y):
		return np.dot(np.random.rand(n, 2), [[x, 0], [0, y]])

	def update(self, sensorReading):
		ps = self.sample(self.ws)
		self.particles = self.diffuse(ps)
		ws = self.reweigh(sensorReading, cov=self.sensorVar)
		self.ws = ws / sum(self.ws)

	def addNoisyParticles(self):
		self.particles[0 : self.nn, ] = self.genParticles(self.nn, self.x, self.y)
		self.ws[0 : self.nn, ] = [0.5] * self.nn

	def sample(self, ws):
		return self.particles[np.random.choice(range(self.n), self.n, p=ws)]

	def reweigh(self, sensorReading, cov=np.eye(2)):
		ws = mvn.pdf(self.particles, mean=sensorReading, cov=cov)
		return (ws / ws.sum())

	def diffuse(self, ps):
		mag = np.eye(2) * self.diffusionMagnitude
		shift = [sum(row) / 2 for row in mag]
		return ps + np.dot(np.random.rand(self.n, 2), mag) - shift

	def consensus(self):
		return np.average(self.particles, axis=0, weights=self.ws)
