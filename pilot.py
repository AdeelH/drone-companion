
class Pilot(object):

	def __init__(self, drone, limits):
		self.drone = drone
		self.maxFb, self.maxAv, self.maxVv, self.maxLr = limits
		self.drone.trim()

	def follow(self, targetOffsetRatio, distRatio, sensorData=(1e3, 1e3, 1e3, 1e3)):
		angularV, verticalV = targetOffsetRatio
		# if too close
		if distRatio < 1:
			# move backward = positive forward tilt
			forwardBackwardTilt = min((1 - distRatio)**2, self.maxFb)
		else:
			# move forward = negative forward tilt
			forwardBackwardTilt = max(-min((distRatio - 1)**2, 1), -self.maxFb)
		fb, lr = self.avoidObstacles(sensorData)
		print(sensorData, fb, lr)
		if abs(forwardBackwardTilt) < 0.05:
			if abs(fb) < 0.05 and abs(lr) < 0.05:
				self.drone.move2(verticalV, angularV)
			else:
				self.drone.move(lr, fb, verticalV, angularV)
		else:
			if abs(fb) < 0.05 and abs(lr) < 0.05:
				self.drone.move(0, forwardBackwardTilt, verticalV, angularV)
			else:
				self.drone.move(lr, fb, verticalV, angularV)

	def avoidObstacles(self, sensorData):
		if sensorData is None:
			return 0, 0
		l, b, r, f = sensorData
		fb = self.avoidObstaclesOnAxis(f, b)
		lr = self.avoidObstaclesOnAxis(l, r)
		return fb, lr

	def avoidObstaclesOnAxis(self, d1, d2):
		if min(d1, d2) < 65:
			if (d1 + d2) < 130 or abs(d1 - d2) < 15:
				return 0
			else:
				if d1 < 65:
					return 0.5 * (0.95**d1)
				return -0.5 * (0.95**d2)
		return 0

	def land(self):
		self.drone.land()

	def takeoff(self):
		self.reset()
		self.drone.trim()
		self.drone.takeoff()

	def hover(self, sensorData=(1e3, 1e3, 1e3, 1e3)):
		fb, lr = self.avoidObstacles(sensorData)
		print(sensorData, fb, lr)
		if abs(fb) < 0.05 and abs(lr) < 0.05:
			self.drone.hover()
		else:
			self.drone.move(lr, fb, 0, 0)

	def reset(self):
		if self.drone.navdata['state']['emergency'] == 1:
			self.drone.reset()
