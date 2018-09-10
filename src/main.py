from parser import OsuFileParser,TimePoint
from position import PositionPlayer,PositionPlayerThread
from click import ClickPlayer,ClickPlayerThread

if __name__ == "__main__":
	parser = OsuFileParser()
	print("Please Input the Osu! file!")
	parser.parse_file(input())

	pp = PositionPlayer(parser.get_list())
	cp = ClickPlayer(parser.get_list())

	position_thread = PositionPlayerThread(pp)
	click_thread = ClickPlayerThread(cp)

	print("The Parser is finished!, Make the Game paused! and Press Enter to start the game")

	pp.begin()
	position_thread.start()
	click_thread.start()
