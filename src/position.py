import time
import win32gui
import win32con
import win32api
import math
from threading import Thread
# right => x
# down  => y

class PositionPlayer:
	def __init__(self, actionList):
		self.actionList = actionList
		self.x = [0,1]
		self.y = [0,1]
		self.index = 0
		self.start_time = 0
		self.handle = win32gui.FindWindow(None, "osu!")
		self.maxx = 512
		self.maxy = 384
		self._PRE_LEFT_MILLSEC = 1
		self.catch_ui()
		self.restart()

	# To restart the player
	def restart(self):
		self.start_time = time.time() * 1000
		self.index = 0
		move_to(actionList[0].x, actionList[0].y)
		self.play()

	def set_start_time(self, start_time):
		self.start_time = start_time
		self.index = 0
		move_to(actionList[0].x, actionList[0].y)
		self.play()
		# To catch the windows of osu!
	def catch_ui(self):
		left,top,right,bottom = win32gui.GetWindowRect(handle)
		self.x = [left, right]
		self.y = [top, bottom]

	def move_to(self, x, y):
		x = int(x / self.maxx * (self.x[1] - self.x[0])) + self.x[0]
		y = int(y / self.maxy * (self.y[1] - self.y[0])) + self.y[0]
		win32api.SetCursorPos((x,y))

	def next_mouse_target(self, ac1, ac2):
		while (True):
			now = time.time() * 1000
			if (now <= ac1.time + self._PRE_LEFT_MILLSEC):
				continue
			if (now >= ac2.time - self._PRE_LEFT_MILLSEC):
				break 

			pos = (now - start_time - ac1.time) / (ac2.time - ac1.time)
			x = ac1.x * (1 - pos) + ac2.x * pos
			y = ac1.y * (1 - pos) + ac2.y * pos

	def play(self):
		n = len(self.actionList)
		while (self.index < n):
			self.next_mouse_target(self.actionList[self.index], self.actionList[self.index + 1])
			self.index += 1

class PositionPlayerThread(Thread):
	def __init__(self, player):
		super(PositionPlayerThread, self).__init__(name = "PositionPlayerThread")
		self.player = player

	def run(self):
		self.player.restart()