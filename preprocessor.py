import numpy as np
import cv2


class Preprocessor(object):

	def __init__(self):
		self.loadCameraParams('config/calibration')

	def loadCameraParams(self, path):
		self.mtx = np.loadtxt('{0}/mtx'.format(path))
		self.dist = np.loadtxt('{0}/dist'.format(path))
		self.newcameramtx = np.loadtxt('{0}/newcameramtx'.format(path))

	def undistort(self, img):
		# undistorted = cv2.undistort(img, self.mtx, self.dist)
		undistorted = cv2.undistort(img, self.mtx, self.dist, None, self.newcameramtx)
		return undistorted
