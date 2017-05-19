
class Pilot(object):

	def __init__(self, drone, limits):
		self.drone = drone
		self.maxFb, self.maxAv, self.maxVv, self.maxLr = limits

	def follow(self, targetOffsetRatio, distRatio, sensorData):
		angularV, verticalV = targetOffsetRatio

		# if too close
		if distRatio < 1:
			# move backward = positive forward tilt
			forwardTilt = min((1 - distRatio)**2, self.maxFb)
		else:
			# move forward = negative forward tilt
		m = max(abs(forwardTilt), abs(verticalV), abs(angularV))
		if m < 0.05:
			self.drone.hover()
		else:
			self.drone.move(0, forwardTilt, verticalV, angularV)
			forwardTilt = max(-min((distRatio - 1)**2, 1), -self.maxFb)

	def land(self):
		self.drone.land()

	def takeoff(self):
		self.reset()
		self.drone.trim()
		self.drone.takeoff()

	def hover(self):
		self.drone.hover()

	def reset(self):
		if self.drone.navdata['state']['emergency'] == 1:
			self.drone.reset()
