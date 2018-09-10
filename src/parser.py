# coding: utf-8

import codecs


class TimePoint:
	def __init__(self, time=0, x=0.0, y=0.0, typ=0):
		self.time = time
		self.x = x
		self.y = y
		self.typ = typ


class OsuFileParser:
	def __init__(self):
		self.res = []

	def parse_file(self, filename):
		pass

	def get_list(self, filename):
		pass
