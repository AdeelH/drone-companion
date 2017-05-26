from numpy import math
from tkinter import *
from PIL import Image, ImageTk
import atexit


class GUI(object):

	def __init__(self, rectCallback, handleUserInput):
		self.rectCallback = rectCallback
		self.handleInput = handleUserInput
		w = 1280
		h = 720
		self.battery_images = [
			Image.open("img/0.png").resize((28, 63)),
			Image.open("img/25.png").resize((28, 63)),
			Image.open("img/50.png").resize((28, 63)),
			Image.open("img/75.png").resize((28, 63)),
			Image.open("img/100.png").resize((28, 63))
		]
		self.origCopter = Image.open("img/copter.png").resize((88, 88))
		self.oldBattery = 100
		self.oldAngle = 0
		self.window = Tk()
		self.window.wm_title("Drone Companion")
		frame = Frame(self.window, width=w, height=h).grid(row=0, column=0, rowspan=3, columnspan=40)
		self.canvas = Canvas(frame, width=w, height=h)
		self.canvas.grid(row=0, column=0, rowspan=3, columnspan=40)

		self.droneImage = self.canvas.create_image(0, 0, anchor=NW)

		self.batteryIcon = self.canvas.create_image(12, 650, anchor=NW)
		self.batteryPercent = self.canvas.create_text(70, 683, font=("Bold", 18), fill='white')

		self.droneIcon = self.canvas.create_image(770, 645, anchor=NW)#

		self.selectionRect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='blue', width=3)
		self.rect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='#38b44a', width=3)
		self.rect2 = self.canvas.create_rectangle(-1, -1, -1, -1, outline='red', width=3)

		self.navDataLabel = self.canvas.create_text(650, 686, font=("Monofonto", 18, "italic"), fill='#00ff78')  # 00ff78 38b44a

		self.recImg = Image.open("img/record.png")
		self.recImg = ImageTk.PhotoImage(self.recImg.resize((71, 64)))
		self.canvas.create_image(1200, 650, image=self.recImg, anchor=NW)
		self.canvas.bind("<Button-1>", self.recordPressed)

		# Bound drag to right mouse button
		self.canvas.bind("<B3-Motion>", self.mouseDragged)
		self.newDrag = True
		self.canvas.bind("<ButtonRelease-3>", self.mouseStopped)

		self.window.bind("<KeyRelease-q>", self.handleInput)
		self.window.bind("<KeyRelease-r>", self.handleInput)
		self.window.bind("<KeyRelease-p>", self.handleInput)
		self.window.bind("<KeyRelease- >", self.handleInput)

		atexit.register(self.handleExit)

	# ----------------------------- DEFINITIONS -------------------------------

	def update(self, frame, navdata):
		self.img_bg = ImageTk.PhotoImage(Image.fromarray(frame))
		self.canvas.itemconfigure(self.droneImage, image=self.img_bg)

		battery, altitude = navdata['battery'], navdata['altitude']
		theta, phi, psi = navdata['theta'], navdata['phi'], navdata['psi']

		if battery != self.oldBattery:
			self.canvas.itemconfigure(self.batteryPercent, text=str(battery) + "%")
			tmp = self.battery_images[int(math.ceil(battery / 25))]
			self.img_battery = ImageTk.PhotoImage(tmp)
			self.canvas.itemconfigure(self.batteryIcon, image=self.img_battery)
			self.oldBattery = battery

		altText = 'Altitude {0} mm'.format(altitude)
		angleText = 'Angles: {1}°, {2}°, {3}°'.format(altitude, theta, phi, psi)
		navdataText = '{0}\n{1}'.format(altText, angleText)
		self.canvas.itemconfigure(self.navDataLabel, text=navdataText)

		if phi != self.oldAngle:
			self.copterImg = self.origCopter
			self.copterImg = self.copterImg.rotate(-phi)
			self.img_copter = ImageTk.PhotoImage(self.copterImg)
			self.canvas.itemconfigure(self.droneIcon, image=self.img_copter)
			self.oldAngle = phi

	def recordPressed(self, event):
		if (1204 < event.x < 1204+self.recImg.width()) and (655 < event.y < 655+self.recImg.height()):
			print("Recording")

	def mouseDragged(self, event):
		if self.newDrag:   # wasReleased
			self.newDrag = False
			self.x0 = event.x
			self.y0 = event.y

		# Draw a rectangle
		self.canvas.coords(self.selectionRect, self.x0, self.y0, event.x, event.y)

	def mouseStopped(self, event):
		if not self.newDrag:
			self.newDrag = True
			self.x1 = event.x
			self.y1 = event.y
			self.canvas.coords(self.selectionRect, (-1, -1, -1, -1))
			self.rectCallback((self.x0, self.y0, self.x1, self.y1))

	def drawRect(self, points1, points2):
		self.canvas.coords(self.rect, points1)
		self.canvas.coords(self.rect2, points2)

	def undrawRects(self):
		self.canvas.coords(self.rect, (-1, -1, -1, -1))
		self.canvas.coords(self.rect2, (-1, -1, -1, -1))

	def handleExit(self):
		try:
			self.window.destroy()
		except:
			pass
