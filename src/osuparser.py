# coding: utf-8

import codecs

class TimePoint:
	MOUSE_NO_ACTION = 0
	MOUSE_DOWN = 1
	MOUSE_UP = 2

	def __init__(self, time=0, x=0.0, y=0.0, typ=0):
		self.time = time
		self.x = x
		self.y = y
		self.typ = typ      # 1-Key down, 2-Key up, 3-Single click
	# END __init__


class OsuFileParser:
	class TimingPoint:
		def __init__(self, time=0, beatlen=0.0):
			self.time = time
			self.beatlen = beatlen
	# END class TimingPoint

	def __init__(self):
		self.res = []
		self.timing_points = []
		self.beatmap_title = ""
		self.beatmap_id = ""
		self.beatmap_set_id = ""
		self.slider_multiplier = 1.4
	# END __init__

	def __parse_attrs(self, props, dict):
		try:
			for item in props:
				colon_index = item.find(':')
				prop, value = item[:colon_index], item[colon_index + 1:]
				if prop in dict:
					setattr(self, dict[prop], value)
		except AttributeError as ex:
			print(ex)
	# END __parse_attrs

	def parse_file(self, filename):
		osu = codecs.open(filename, encoding='utf-8')
		line = ""

		# osu file version
		osu_ver = int(osu.readline()[17:])
		if osu_ver < 12:
			print('Version lower than 12 currently not supported')
			return

		li = ""
		line = osu.readline()
		while line != "":
			while line != "":
				li = line.strip()
				if len(li) > 0 and li[0] == '[':
					break
				line = osu.readline()
			tag = li[1:-1]
			props = []

			line = osu.readline()
			while line != "":
				li = line.strip()
				if li == "" or li[0] == '[':
					break
				if len(li) > 0:
					props.append(li)
				line = osu.readline()

			if tag == 'General':
				pass
			elif tag == 'Editor':
				pass
			elif tag == 'Metadata':
				self.__parse_attrs(props, {
					'Title': 'beatmap_title',
					'BeatmapID': 'beatmap_id',
					'BeatmapSetID': 'beatmap_set_id'
				})
			elif tag == 'Difficulty':
				self.__parse_attrs(props, {
					'SliderMultiplier': 'slider_multiplier',
				})
			elif tag == 'Events':
				pass
			elif tag == 'TimingPoints':
				self.timing_points = []
				last_positive = 0.0
				for item in props:
					prop = item.split(',')
					if len(prop) < 8:
						print('Unrecognized TimingPoint format')
						return
					time = int(prop[0])
					beatlen = float(prop[1])
					if beatlen < 0:
						beatlen = -beatlen / 100 * last_positive
					else:
						last_positive = beatlen
					self.timing_points.append(OsuFileParser.TimingPoint(time, beatlen))
			elif tag == 'Colours':
				pass
			elif tag == 'HitObjects':
				self.res = []
				for item in props:
					prop = item.split(',')
					x = int(prop[0])
					y = int(prop[1])
					time = int(prop[2])
					typ = int(prop[3])
					self.res.append(TimePoint(time, x, y, TimePoint.MOUSE_NO_ACTION))
			else:
				print('Unrecognized tag ' + tag)
				return
			# END if
		# END while
	# END parse_file

	def get_list(self):
		return self.res
	# END get_list
