import struct
import socket
import threading


class SensorDataReceiver(threading.Thread):

	def __init__(self, port, callback):
		threading.Thread.__init__(self)
		self.callback = callback
		self.stopping = False
		self.port = port

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', self.port))
		while not self.stopping:
			try:
				data, addr = sock.recvfrom(8)
				self.callback(struct.unpack('d', data)[0])
			except:
				self.stopping = True
				sock.close()