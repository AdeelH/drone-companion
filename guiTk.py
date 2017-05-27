from numpy import math
from tkinter import *
from PIL import Image, ImageTk
import atexit


class GUI(object):

	def __init__(self, imageScaleFactor, rectCallback, inputCallback):
		self.imageScaleFactor = imageScaleFactor
		self.rectCallback = rectCallback
		self.inputCallback = inputCallback
		w, h = 1280, 720

		self.window = Tk()
		self.window.wm_title("Drone Companion")
		frame = Frame(self.window, width=w, height=h).grid(row=0, column=0, rowspan=3, columnspan=40)
		self.canvas = Canvas(frame, width=w, height=h)
		self.canvas.grid(row=0, column=0, rowspan=3, columnspan=40)

		self.initElements()
		self.initEventListeners()

		self.oldBattery = 100
		self.oldAngle = 0
		self.dragging = False

	def initElements(self):
		self.video = self.canvas.create_image(0, 0, anchor=NW)
		self.initRects()
		self.initNavDataDisplay()
		self.initButtons()

	def initEventListeners(self):
		self.canvas.bind("<B3-Motion>", self.mouseDragged)
		self.canvas.bind("<ButtonRelease-3>", self.mouseStopped)
		self.window.bind("<KeyRelease>", lambda evt: self.inputCallback(evt.char))
		atexit.register(self.handleExit)

	def initNavDataDisplay(self):
		self.battery_images = [
			Image.open("img/0.png").resize((28, 63)),
			Image.open("img/25.png").resize((28, 63)),
			Image.open("img/50.png").resize((28, 63)),
			Image.open("img/75.png").resize((28, 63)),
			Image.open("img/100.png").resize((28, 63))
		]
		self.batteryIcon = self.canvas.create_image(12, 650, anchor=NW)
		self.batteryPercent = self.canvas.create_text(70, 683, font=("Bold", 18), fill='white')

		self.droneIconImage = Image.open("img/copter.png").resize((88, 88))
		self.droneIcon = self.canvas.create_image(770, 645, anchor=NW)

		self.navDataLabel = self.canvas.create_text(650, 686, font=("Monofonto", 18, "italic"), fill='#00ff78')

	def initRects(self):
		self.selectionRect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='blue', width=3)
		self.trackingRect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='red', width=3)
		self.smoothingRect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='#38b44a', width=3)

	def initButtons(self):
		self.recImg = Image.open("img/record.png")
		self.recImg = ImageTk.PhotoImage(self.recImg.resize((71, 64)))
		recImgId = self.canvas.create_image(1200, 650, image=self.recImg, anchor=NW)
		self.canvas.tag_bind(recImgId, "<Button-1>", self.recordPressed)

	def update(self, frame, navdata):
		self.img_bg = ImageTk.PhotoImage(Image.fromarray(frame))
		self.canvas.itemconfigure(self.video, image=self.img_bg)
		self.updateNavDataDisplay(navdata)

	def updateNavDataDisplay(self, navdata):
		battery, altitude = navdata['battery'], navdata['altitude']
		theta, phi, psi = navdata['theta'], navdata['phi'], navdata['psi']

		altText = 'Altitude {0} mm'.format(altitude)
		angleText = 'Angles: {1}°, {2}°, {3}°'.format(altitude, theta, phi, psi)
		navdataText = '{0}\n{1}'.format(altText, angleText)

		self.canvas.itemconfigure(self.navDataLabel, text=navdataText)
		self.updateBatteryDisplay(battery)
		self.updateAngleVisualization(phi)

	def updateBatteryDisplay(self, battery):
		if battery != self.oldBattery:
			self.canvas.itemconfigure(self.batteryPercent, text=str(battery) + "%")
			tmp = self.battery_images[int(math.ceil(battery / 25))]
			self.img_battery = ImageTk.PhotoImage(tmp)
			self.canvas.itemconfigure(self.batteryIcon, image=self.img_battery)
			self.oldBattery = battery

	def updateAngleVisualization(self, phi):
		if phi != self.oldAngle:
			self.copterImg = self.droneIconImage
			self.copterImg = self.copterImg.rotate(-phi)
			self.img_copter = ImageTk.PhotoImage(self.copterImg)
			self.canvas.itemconfigure(self.droneIcon, image=self.img_copter)
			self.oldAngle = phi

	def recordPressed(self, event):
		self.inputCallback('r')

	def mouseDragged(self, event):
		if not self.dragging:
			self.dragging = True
			self.x0, self.y0 = event.x, event.y
		self.canvas.coords(self.selectionRect, self.x0, self.y0, event.x, event.y)

	def mouseStopped(self, event):
		if self.dragging:
			self.dragging = False
			self.canvas.coords(self.selectionRect, (-1, -1, -1, -1))

			x0, y0 = self.x0 / self.imageScaleFactor, self.y0 / self.imageScaleFactor
			x1, y1 = event.x / self.imageScaleFactor, event.y / self.imageScaleFactor
			if x0 > x1:
				x0, x1 = x1, x0
			if y0 > y1:
				y0, y1 = y1, y0
			self.rectCallback((x0, y0, x1, y1))

	def drawTrackingRect(self, rect):
		self.canvas.coords(self.trackingRect, tuple([self.imageScaleFactor * c for c in rect]))

	def drawSmoothingRect(self, rect):
		self.canvas.coords(self.smoothingRect, tuple([self.imageScaleFactor * c for c in rect]))

	def undrawRects(self):
		self.canvas.coords(self.trackingRect, (-1, -1, -1, -1))
		self.canvas.coords(self.smoothingRect, (-1, -1, -1, -1))

	def handleExit(self):
		try:
			self.window.destroy()
		except:
			pass
