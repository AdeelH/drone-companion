import traceback
from droneCompanion import DroneCompanion


if __name__ == '__main__':
	try:
		dc = DroneCompanion()
		dc.start()
	except Exception:
		traceback.print_exc()
		try:
			dc.abort()
		except:
			pass
