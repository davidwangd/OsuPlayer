from parser import OsuFileParser,TimePoint
from position import PositionPlayer,PositionPlayerThread
from click import ClickPlayer,ClickPlayerThread

if __name__ == "__main__":
	parser = OsuFileParser()
	print("Please Input the Osu! file!")
	parser.parse_file(input())

	position_thread = PositionPlayerThread(PositionPlayer(parser.get_list()))
	click_thread = ClickPlayerThread(ClickPlayer(parser.get_list()))

	print("The Parser is finished!, Press Enter to start the game")

	position_thread.start()
	click_thread.start()

	