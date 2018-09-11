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
		self._CLICK_TIME = 50
		self.maxtime = -1

	def restart(self):
		self.start_time = time.time() * 1000
		self.play()

	def set_start_time(self, start_time):
		self.start_time = start_time
		self.play()

	def play(self):
		i = 0
		flag = 0
		while (i < len(self.actionList)):
			now = time.time() * 1000 - self.start_time
			if (self.maxtime != -1 and now > self.maxtime * 1000):
				break
			if (self.actionList[i].typ == 0):
				i += 1
			elif (now > self.actionList[i].time - self._CLICK_TIME and self.actionList[i].typ  == 1):
				if (flag == 0):
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
					print("Down ",now)
					flag = 1
				i += 1
			elif (now > self.actionList[i].time + self._CLICK_TIME and self.actionList[i].typ  == 2):
				if (flag == 1):
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
					print("Up ", now)
					flag = 0
				i += 1
			elif (now > self.actionList[i].time and self.actionList[i].typ == 3):
				win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
				time.sleep(0.05)
				win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
				i += 1
class ClickPlayerThread(Thread):
	def __init__(self, player):
		super(ClickPlayerThread, self).__init__(name = "ClickPlayerThread")
		self.player = player

	def run(self):
		self.player.restart()

