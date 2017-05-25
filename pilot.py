
class Pilot(object):

	def __init__(self, drone, limits):
		self.drone = drone
		self.maxFb, self.maxAv, self.maxVv, self.maxLr = limits
		self.drone.trim()

	def follow(self, targetOffsetRatio, distRatio, sensorData):
		angularV, verticalV = targetOffsetRatio

		# if too close
		if distRatio < 1:
			# move backward = positive forward tilt
			forwardTilt = min((1 - distRatio)**2, self.maxFb)
		else:
			# move forward = negative forward tilt
			forwardTilt = max(-min((distRatio - 1)**2, 1), -self.maxFb)
		print(forwardTilt, angularV, verticalV)
		if abs(forwardTilt) < 0.05:
			self.drone.move2(0, forwardTilt, verticalV, angularV)
		else:
			self.drone.move(0, forwardTilt, verticalV, angularV)

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
