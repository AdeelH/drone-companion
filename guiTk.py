from numpy import math
from tkinter import *
from PIL import Image, ImageTk
import atexit


class GUI(object):

	def __init__(self, res, rectCallback, handleUserInput):
		self.rectCallback = rectCallback
		self.handleInput = handleUserInput
		w = 1280
		h = 720
		self.battery_images = [
			Image.open("img/0.png"),
			Image.open("img/25.png"),
			Image.open("img/50.png"),
			Image.open("img/75.png"),
			Image.open("img/100.png")
		]
		self.window = Tk()
		self.window.wm_title("Drone Companion")
		frame = Frame(self.window, width=w, height=h).grid(row=0, column=0, rowspan=3, columnspan=40)
		self.canvas = Canvas(frame, width=w, height=h)
		self.canvas.grid(row=0, column=0, rowspan=3, columnspan=40)

		self.droneImage = self.canvas.create_image(0, 0, anchor=NW)

		self.batteryIcon = self.canvas.create_image(12, 650, anchor=NW)
		self.batteryPercent = self.canvas.create_text(70, 682, font=("Bold", 18), fill='white')
		self.updateBattery(0)

		self.rect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='green', width=3)
		self.rect2 = self.canvas.create_rectangle(-1, -1, -1, -1, outline='red', width=3)

		self.canvas.create_text(645, 685, font=("Monofonto", 18), fill='green', text="Altitude: 1000ft")

		self.recImg = Image.open("img/record.png")
		self.recImg = ImageTk.PhotoImage(self.recImg.resize((int(self.recImg.width / 9), int(self.recImg.height / 9))))
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

        atexit.register(handleExit)

		###############################DEFINITIONS###############################

	def display(self, frame):
		self.img_bg = ImageTk.PhotoImage(Image.fromarray(frame))
		self.canvas.itemconfigure(self.droneImage, image=self.img_bg)
		return

	def updateBattery(self, battery):
		self.canvas.itemconfigure(self.batteryPercent, text=str(battery) + "%")
		tmp = self.battery_images[int(math.ceil(battery / 25))]
		self.img_battery = ImageTk.PhotoImage(tmp.resize((int(tmp.width / 7), int(tmp.height / 7))))
		self.canvas.itemconfigure(self.batteryIcon, image=self.img_battery)

	def recordPressed(self, event):
		if (1204 < event.x < 1204+self.recImg.width()) and (655 < event.y < 655+self.recImg.height()):
			print("Recording")

	def mouseDragged(self, event):
		if self.newDrag:   # wasReleased
			self.newDrag = False
			self.x0 = event.x
			self.y0 = event.y

		# Draw a rectangle
		self.canvas.coords(self.rect, self.x0, self.y0, event.x, event.y)

	def mouseStopped(self, event):
		if not self.newDrag:
			self.newDrag = True
			self.x1 = event.x
			self.y1 = event.y
			self.rectCallback((self.x0, self.y0, self.x1, self.y1))

	def drawRect(self, points1, points2):
		self.canvas.coords(self.rect, points1)
		self.canvas.coords(self.rect2, points2)

    def handleExit(self):
        self.window.destroy()