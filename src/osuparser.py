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
	SPINNER_START_DELAY = 10
	SPINNER_RADIUS = 50
	SPINNER_ROTATER = np.e ** (1j/4 * np.pi)
	BEZIER_STEPS = 10
	EPSILON = 1e-4

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
		elif curve_type == 'P' or curve_type == 'B':
			points = int(np.ceil(duration / OsuFileParser.INTERPOLATION_INTERVAL))
			if curve_type == 'P':
				# Calculate center, radius & center angle
				c0, c1 = controls[0].split(':'), controls[1].split(':')
				p0 = x + y * 1j
				p1 = float(c0[0]) + float(c0[1]) * 1j
				p2 = float(c1[0]) + float(c1[1]) * 1j
				w = (p2 - p0) / (p1 - p0)
				center = (p1 - p0) * (w - abs(w)**2) / (2j * w.imag) + p0;
				radius = p0 - center
				center_angle = 2 * (np.arcsin(abs(p1 - p0) / (2 * abs(radius))) + np.arcsin(abs(p2 - p1) / (2 * abs(radius))))
				direction = np.sign((p1 - p0).real * (p2 - p1).imag - (p1 - p0).imag * (p2 - p1).real)
				# Do interpolation
				interpolation = [p0]
				for i in range(1, points + 1):
					angle = direction * (center_angle * i / points)
					interpolation.append(radius * (np.cos(angle) + np.sin(angle) * 1j) + center);
			else:
				controls_len = len(controls)
				bezier = [x + y * 1j]
				curve_lens = []
				curve_points = []
				for i in range(controls_len):
					c = controls[i].split(':')
					bezier.append(float(c[0]) + float(c[1]) * 1j)
					if i == controls_len - 1 or controls[i] == controls[i + 1]:
						n = len(bezier)
						seg = [bezier[0]]
						for v in range(OsuFileParser.BEZIER_STEPS):
							intpl = bezier.copy()
							next_interpolation = []
							t = (v + 1) / OsuFileParser.BEZIER_STEPS
							for j in range(n - 1):
								for k in range(n - 1 - j):
									next_interpolation.append(intpl[k] * (1 - t) + intpl[k + 1] * t)
								intpl = next_interpolation
								next_interpolation = []
							seg.append(intpl[0])
						curve_points.append(seg)
						curve_len = 0
						for i in range(OsuFileParser.BEZIER_STEPS):
							curve_len += abs(seg[i + 1] - seg[i])
						curve_lens.append(curve_len)
						bezier.clear()
					# END if
				# END for
				n = len(curve_lens)
				curve_tot_len = sum(curve_lens)
				interpolation = [x + y * 1j]
				for i in range(1, points + 1):
					expect_len = curve_tot_len * i / points - OsuFileParser.EPSILON
					current_len = 0
					p = -1
					for j in range(n):
						if (current_len + curve_lens[j] >= expect_len):
							for k in range(OsuFileParser.BEZIER_STEPS):
								small_seg = abs(curve_points[j][k + 1] - curve_points[j][k])
								if (current_len + small_seg >= expect_len):
									t = (expect_len - current_len) / small_seg
									p = curve_points[j][k] * (1 - t) + curve_points[j][k + 1] * t;
									break
								else:
									current_len += small_seg
							if p != -1:
								break
						else:
							current_len += curve_lens[j]
					# END for
					interpolation.append(p)
				# END for
			# END if
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
					if len(self.timing_points) > 0 and self.timing_points[-1].time == time:
						self.timing_points[-1] = OsuFileParser.TimingPoint(time, beatlen)
					else:
						self.timing_points.append(OsuFileParser.TimingPoint(time, beatlen))
				# END for
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
						endTime = int(prop[5])
						time += OsuFileParser.SPINNER_START_DELAY
						i = 0
						point_vec = OsuFileParser.SPINNER_RADIUS + 0j
						while time < endTime:
							tp = TimePoint(time, x + point_vec.real, y + point_vec.imag, TimePoint.MOUSE_NO_ACTION)
							if i == 0:
								tp.typ += TimePoint.MOUSE_DOWN
							if time + OsuFileParser.INTERPOLATION_INTERVAL >= endTime:
								tp.typ += TimePoint.MOUSE_UP
							i += 1
							self.res.append(tp)
							time += OsuFileParser.INTERPOLATION_INTERVAL / 2
							point_vec *= OsuFileParser.SPINNER_ROTATER
						# END while
					else:
						print('Unrecognized HitObject type %d)' % typ)
					# END if
				# END for
			else:
				print('Unrecognized tag ' + tag)
				return
			# END if
		# END while
	# END parse_file

	def get_list(self):
		return self.res
	# END get_list
