import struct
import socket
import threading
import select
import time


class SensorDataReceiver(threading.Thread):

	def __init__(self, port, callback):
		threading.Thread.__init__(self)
		self.callback = callback
		self.stopping = False
		self.port = port

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setblocking(False)
		sock.bind(('', self.port))
		while not self.stopping:
			time.sleep(0)
			inputready, _, _ = select.select([sock], [], [], 0)
			if len(inputready) < 1:
				continue
			while True:
				try:
					data, addr = sock.recvfrom(16)
				except IOError:
					# we consumed every packet from the socket and continue with the last one
					break
			self.callback(struct.unpack('iiii', data))
		sock.close()

	def stop(self):
		self.stopping = True
