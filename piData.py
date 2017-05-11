import socket
import threading
import struct

class PiThread(threading.Thread):

	def __init__(self, callback):
		threading.Thread.__init__(self)
		self.callback = callback
		self.stopping = False

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', 3000))
		print('listening')

		try:
			while not self.stopping:
				data, _ = sock.recvfrom(8)
				if len(data) > 0:
					self.callback(struct.unpack('d', data)[0])
		except:
			sock.close()
