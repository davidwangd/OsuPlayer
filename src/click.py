# coding : utf-8

import time
import win32gui
import win32con
import win32api
import math
from threading import Thread

class ClickPlayer:
	def __init__(self, actionList):
		self.actionList = actionList
		self.start_time = 0
		self._CLICK_TIME = 20

	def restart(self):
		self.start_time = time.time() * 1000
		self.play()

	def set_start_time(self, start_time):
		self.start_time = start_time
		self.play()

	def play():
		i = 0

		while (i < len(self.actionList)):
			now = time.time() * 1000
			if (self.actionList[i].typ == 0):
				i += 1
			elif (now < self.actionList[i].time - self._CLICK_TIME and (self.actionList[i].time & 1) == 1):
				win32api.mouse_event(win32con.MOUSEEVENT_LEFTDOWN, 0, 0, 0, 0)
				i += 1
			elif (now > self.actionList[i].time + self._CLICK_TIME and (self.actionList[i].time & 2) == 1):
				win32api.mouse_event(win32con.MOUSEEVENT_LEFTUP, 0, 0, 0, 0)
				i += 1

class ClickPlayerThread(Thread):
	def __init__(self, player):
		super(ClickPlayerThread, self).__init__(name = "ClickPlayerThread")
		self.player = player

	def run(self):
		self.player.restart()

