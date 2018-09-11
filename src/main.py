from osuparser import OsuFileParser,TimePoint
from position import PositionPlayer,PositionPlayerThread
from click import ClickPlayer,ClickPlayerThread
import win32gui
import codecs
import sys
import time
if __name__ == "__main__":
	if (len(sys.argv) == 1):
		parser = OsuFileParser()
		print("Please Input the Osu! file!")
		parser.parse_file(input())

		handle = win32gui.FindWindow(None, "osu!")
		class_name = win32gui.GetClassName(handle)

		for t in parser.get_list():
			print([t.x,t.y,t.time,t.typ])

		pp = PositionPlayer(parser.get_list(), class_name)
		cp = ClickPlayer(parser.get_list())

		position_thread = PositionPlayerThread(pp)
		click_thread = ClickPlayerThread(cp)


		print("The Parser is finished!, Make the map selected. ")
		print(" input the maxtime(seconds) you want the engine to play for you, -1 or nothing represent the whole map")
		maxtime = -1
		try:
			maxtime = int(input())
		except Error as e:
			maxtime = -1

		print("Input a experience acording origin number, the max the number is, the early the orgin will come")
		dim_threshold = float(input())

		print("Input First Sleep Time")
		sl = float(input())
		

		pp.maxtime = maxtime
		cp.maxtime = maxtime
		pp.begin2()
		if (sl > 0):
			time.sleep(sl)
		position_thread.start()
		click_thread.start()

	elif (len(sys.argv) == 2):
		file = codecs.open(sys.argv[1])
		lines = file.readlines()
		parser = OsuFileParser()
		parser.parse_file(lines[0].strip())
		handle = win32gui.FindWindow(None, "osu!")
		class_name = win32gui.GetClassName(handle)

		for t in parser.get_list():
			print([t.x,t.y,t.time,t.typ])

		pp = PositionPlayer(parser.get_list(), class_name)
		cp = ClickPlayer(parser.get_list())

		position_thread = PositionPlayerThread(pp)
		click_thread = ClickPlayerThread(cp)
		maxtime = int(lines[1])
		dim_threshold = float(lines[2])
		sl = float(lines[3])
		

		pp.maxtime = maxtime
		cp.maxtime = maxtime
		pp.dim_threshold = dim_threshold
		pp.begin2()
		if (sl > 0):
			time.sleep(sl)
		else:
			pp.padding = -1000 * sl
			cp.padding = -1000 * sl

		print("\n\n*****************Begin*****************\n\n")
		position_thread.start()
		click_thread.start()
