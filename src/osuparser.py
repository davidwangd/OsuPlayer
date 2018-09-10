# coding: utf-8

import codecs
import numpy as np

class TimePoint:
	MOUSE_NO_ACTION = 0
	MOUSE_DOWN = 1
	MOUSE_UP = 2
	MOUSE_CLICK = MOUSE_DOWN | MOUSE_UP

	def __init__(self, time=0, x=0.0, y=0.0, typ=0):
		self.time = time
		self.x = x
		self.y = y
		self.typ = typ
	# END __init__

	def __str__(self):
		type_arr = ['-', 'down', 'up', 'click']
		type_str = 'INVALID'
		if 0 <= self.typ <= 3:
			type_str = type_arr[self.typ]
		return 'time %d: (%d, %d) %s' % (self.time, self.x, self.y, type_str)


class OsuFileParser:
	INTERPOLATION_INTERVAL = 50

	TYPE_CIRCLE = 1
	TYPE_SLIDER = 2
	TYPE_SPINNER = 8

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
					attr, typ = dict[prop]
					if (typ == 'str'):
						setattr(self, attr, value)
					elif (typ == 'int'):
						setattr(self, attr, int(value))
					elif (typ == 'float'):
						setattr(self, attr, float(value))
		except AttributeError as ex:
			print(ex)
		except TypeError as ex:
			print(ex)
	# END __parse_attrs

	def __interpolate_slider(self, x, y, slider, repeats, time, duration):
		slider_res = [TimePoint(time, x, y, TimePoint.MOUSE_DOWN)]

		curve_type = slider[0]
		controls = slider[2:].split('|')

		if curve_type == 'L':
			another_end = controls[0].split(':')
			ends = [(int(another_end[0]), int(another_end[1])), (x, y)]
			for i in range(repeats):
				reach_time = int(round(time + duration * (i + 1)))
				reach_end = ends[i % 2]
				mouse_action = TimePoint.MOUSE_NO_ACTION if i < repeats - 1 else TimePoint.MOUSE_UP
				slider_res.append(TimePoint(reach_time, reach_end[0], reach_end[1], mouse_action))
		elif curve_type == 'P':
			# Calculate center, radius & center angle
			c0, c1 = controls[0].split(':'), controls[1].split(':')
			p0 = x + y * 1j
			p1 = float(c0[0]) + float(c0[1]) * 1j
			p2 = float(c1[0]) + float(c1[1]) * 1j
			w = (p2 - p0) / (p1 - p0)
			center = (p1 - p0) * (w - abs(w)**2) / (2j * w.imag) + p0;
			radius = p0 - center
			center_angle = 2 * np.arcsin(abs(p2 - p0) / (2 * abs(radius)))
			direction = np.sign(radius.real * (p2 - p0).imag - radius.imag * (p2 - p0).real)
			# Do interpolation
			interpolation = [p0]
			points = int(np.ceil(duration / OsuFileParser.INTERPOLATION_INTERVAL))
			for i in range(1, points + 1):
				angle = direction * (center_angle * i / points)
				interpolation.append(radius * (np.cos(angle) + np.sin(angle) * 1j) + center);
			base_duration = duration / points
			for i in range(repeats):
				if i % 2 == 0:
					for j in range(1, points + 1):
						time += base_duration
						p = interpolation[j]
						slider_res.append(TimePoint(int(round(time)), p.real, p.imag, TimePoint.MOUSE_NO_ACTION))
				else:
					for j in range(points - 1, -1, -1):
						time += base_duration
						p = interpolation[j]
						slider_res.append(TimePoint(int(round(time)), p.real, p.imag, TimePoint.MOUSE_NO_ACTION))
			end_point = slider_res[-1]
			end_point.typ = TimePoint.MOUSE_UP
			slider_res[-1] = end_point
		elif curve_type == 'B':
			pass
		elif curve_type == 'C':
			print('C-type is deprecated')
		else:
			print('Unrecognized curve type %s' % curve_type)
			return []

		return slider_res

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
					'Title': ('beatmap_title', 'str'),
					'BeatmapID': ('beatmap_id', 'str'),
					'BeatmapSetID': ('beatmap_set_id', 'str')
				})
			elif tag == 'Difficulty':
				self.__parse_attrs(props, {
					'SliderMultiplier': ('slider_multiplier', 'float')
				})
			elif tag == 'Events':
				pass
			elif tag == 'TimingPoints':
				self.timing_points = []
				last_positive = 0.0
				for item in props:
					prop = item.split(',')
					if len(prop) < 8:
						print('Unrecognized TimingPoint %s' % item)
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
				time_point = 0
				for item in props:
					prop = item.split(',')
					x = int(prop[0])
					y = int(prop[1])
					time = int(prop[2])
					typ = int(prop[3])

					while time_point < len(self.timing_points) - 1:
						if self.timing_points[time_point + 1].time < time:
							time_point += 1
						else:
							break
					# END while

					if typ & OsuFileParser.TYPE_CIRCLE > 0:
						self.res.append(TimePoint(time, x, y, TimePoint.MOUSE_CLICK))
					elif typ & OsuFileParser.TYPE_SLIDER > 0:
						slider = prop[5]
						repeats = int(prop[6])
						pixlen = float(prop[7])
						beatlen = self.timing_points[time_point].beatlen
						duration = pixlen / (100 * self.slider_multiplier) * beatlen
						self.res += self.__interpolate_slider(x, y, slider, repeats, time, duration)
					elif typ & OsuFileParser.TYPE_SPINNER > 0:
						pass
					else:
						print('Unrecognized HitObject type %d)' % typ)
			else:
				print('Unrecognized tag ' + tag)
				return
			# END if
		# END while
	# END parse_file

	def get_list(self):
		return self.res
	# END get_list
