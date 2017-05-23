import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk


class GUI(object):

	def __init__(self, res, rectCallback, windowName='vid'):
		w, h = res
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
		self.canvas = tkinter.Canvas(frame, width=w, height=h)
		self.canvas.grid(row=0, column=0, rowspan=3, columnspan=40)

		self.droneImage = canvas.create_image(0, 0, anchor=NW)

		self.batteryIcon = canvas.create_image(12, 290, anchor=NW)
		self.batteryPercent = canvas.create_text(70, 322, font=("Bold", 18), fill='white')

		recImg = Image.open("record.png")
		recImg = ImageTk.PhotoImage(recImg.resize((int(recImg.width / 9), int(recImg.height / 9))))
		self.canvas.create_image(600, 290, image=recImg, anchor=NW)
		canvas.bind("<Button-1>", self.recordPressed)

		self.updateBattery(0)

		# Bound drag to right mouse button
		self.canvas.bind("<B3-Motion>", self.mouseDragged)
		self.canvas.bind("<ButtonRelease-3>", self.mouseStopped)
		self.rect = self.canvas.create_rectangle(-1, -1, -1, -1, outline='green', width=3)

	def display(self, frame):
		self.img_bg = frame
		canvas.itemconfigure(droneImage, image=self.img_bg)
		return

	def updateBattery(self, battery):
		self.canvas.itemconfigure(self.batteryPercent, text=str(battery) + "%")
		tmp = battery_images[int(math.ceil(battery / 25))]
		self.img_battery = ImageTk.PhotoImage(tmp.resize((int(tmp.width / 7), int(tmp.height / 7))))
		self.canvas.itemconfigure(batteryIcon, image=img_battery)

	def recordPressed(self, event):
		if (600 < event.x < 600 + self.recImg.width()) and (290 < event.y < 290 + self.recImg.height()):
			print("Recording")

	def mouseDragged(event):
		if self.newDrag:   # wasReleased
			self.newDrag = False
			self.startX = event.x
			self.startY = event.y

		# Draw a rectangle
		self.canvas.coords(self.myrect, self.startX, self.startY, event.x, event.y)
		print("Stahp it! " + str(event.x) + " " + str(event.y))

	def mouseStopped(event):
		if not self.newDrag:
			global endX, endY
			self.newDrag = True
			endX = event.x
			endY = event.y
			print(str(self.startX) + " " + str(self.startY) + " " + str(endX) + " " + str(endY))

	def close(self):
		self.window.destroy()
