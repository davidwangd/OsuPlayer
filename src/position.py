import time
import win32gui
import win32con
import win32api
import math
from threading import Thread
from PIL import ImageGrab
from PIL import Image

# right => x
# down  => y

def calc(typ):
	if typ == 1:
		return -20
	elif typ == 2:
		return 20
	else:
		return 0

class PositionPlayer:
	def __init__(self, actionList, class_name):
		self.actionList = actionList
		self.x = [0,1]
		self.y = [0,1]
		self.index = 0
		self.start_time = 0
		self.class_name = class_name
		self.handle = win32gui.FindWindow(self.class_name, None)
		self.maxx = 512
		self.maxy = 384
		self._PRE_LEFT_MILLSEC = 1
		self._BEFORE_RESTART = 1.95

		self._XK = 0.6
		self._XB = 0.26
		self._YK = 0.8
		self._YB = 0.135
		self.dim_threshold = 12

		self.catch_ui()

		self.maxtime = -1

	# This Function is dropped!
	def begin(self):
		self.move_to(1.2 * self.maxx,self.maxy)
		# thank to the strange behaviou of osu! we have to make it like this
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
		time.sleep(0.3)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

		time.sleep(3)

		win32api.keybd_event(27,0,0,0)
		time.sleep(0.1)
		win32api.keybd_event(27,0, win32con.KEYEVENTF_KEYUP, 0)
		time.sleep(1)

		self.move_to(self.maxx/2, self.maxy/2)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
		time.sleep(0.3)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


#		time.sleep(1)
#		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#		time.sleep(0.3)
#		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
		
#		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#		time.sleep(0.3)
#		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

		time.sleep(self._BEFORE_RESTART)

	def begin2(self):
		self.move_to(1.2 * self.maxx,self.maxy)
		# thank to the strange behaviou of osu! we have to make it like this
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
		time.sleep(0.3)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

		x0 = int(0.88 * self.x[1] + 0.12 * self.x[0])
		x1 = int(0.98 * self.x[1] + 0.02 * self.x[0])
		y0 = int(0.48 * self.y[1] + 0.52 * self.y[0])
		y1 = int(0.52 * self.y[1] + 0.48 * self.y[0])

		im = Image.new("RGB",(100,100))
		w = x1 - x0
		h = y1 - y0

		while (True):
			im = ImageGrab.grab((x0,y0,x1,y1))
			pix = im.load()
			cnt = 0
			for i in range(w):
				for j in range(h):
					r, g, b = pix[i, j]
					cnt += r + g + b
			cnt /= h * w * 3
			if (cnt < self.dim_threshold):
				break
			# print(cnt)

		im.save("last.jpg")

	# To restart the player
	def restart(self):
		self.start_time = time.time() * 1000
		self.index = 0
		self.move_to(self.actionList[0].x, self.actionList[0].y)
		self.play()

	def set_start_time(self, start_time):
		self.start_time = start_time
		self.index = 0
		self.move_to(self.actionList[0].x, self.actionList[0].y)
		self.play()
		# To catch the windows of osu!
	def catch_ui(self):
		left,top,right,bottom = win32gui.GetWindowRect(self.handle)
		self.x = [left, right]
		self.y = [top, bottom]

	def move_to(self, x, y):
	#	print((x,y))
		x = (x / self.maxx * (self.x[1] - self.x[0])) + self.x[0]
		y = (y / self.maxy * (self.y[1] - self.y[0])) + self.y[0]

		x = int(x * self._XK + self._XB * (self.x[1] - self.x[0]))
		y = int(y * self._YK + self._YB * (self.y[1] - self.y[0]))
		# print((x,y))
		win32api.SetCursorPos((x,y))

	def next_mouse_target(self, ac1, ac2):

	#	print([ac1.x,ac1.y,ac2.x,ac2.y])
		t1 = ac1.time
		t2 = ac2.time 
		# to prevent the last error
		if (ac1.typ == 2):
			t1 += 30

		while (True):
			now = time.time() * 1000 - self.start_time
			# Debug
			if (self.maxtime != -1 and now > self.maxtime * 1000):
				break

			if (now <= t1 + self._PRE_LEFT_MILLSEC):
				continue
			if (now >= t2 - self._PRE_LEFT_MILLSEC):
				break 

			pos = (now - t1) / (t2 - t1)
			x = ac1.x * (1 - pos) + ac2.x * pos
			y = ac1.y * (1 - pos) + ac2.y * pos
			# print([pos,x,y])
			self.move_to(x, y)

	def play(self):
		n = len(self.actionList)
		while (self.index < n - 1):
			self.next_mouse_target(self.actionList[self.index], self.actionList[self.index + 1])
			self.index += 1

class PositionPlayerThread(Thread):
	def __init__(self, player):
		super(PositionPlayerThread, self).__init__(name = "PositionPlayerThread")
		self.player = player

	def run(self):
		self.player.restart()


if __name__ == "__main__":
	

	lis = [ TimePoint(1000,256,192), TimePoint(2000,356,192), TimePoint(3000,156,192), TimePoint(4000,256,92), TimePoint(5000,256,292) ]

	a = PositionPlayer(lis)
	a.restart()