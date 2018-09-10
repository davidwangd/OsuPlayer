from osuparser import OsuFileParser,TimePoint
from position import PositionPlayer,PositionPlayerThread
from click import ClickPlayer,ClickPlayerThread
import win32gui

if __name__ == "__main__":

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


	print("The Parser is finished!, Make the Game paused! and Press Enter to start the game")
	input()

	pp.begin()
	position_thread.start()
	click_thread.start()
