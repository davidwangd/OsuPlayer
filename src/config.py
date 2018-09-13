import codecs


class Config:
	def __init__(self):
		file = codecs.open("config.ini","r","utf-8")
		self.dict = {}
		if (file != None):
			for line in file.readlines():
				if line.find("=") != -1:
					self.dict.update({line.split("=")[0]:float(line.split("=")[1])})
			file.close()
		else:
			self.dict = {"_XB":0.0, "_YB":0.0}

	def get(self, key):
		if (key in self.dict.keys()):
			return [self.dict.get(key), True]
		print("No such value of ", key)
		return [0, False]

	def dump(self):
		file = codecs.open("config.ini","w","utf-8")
		for key in self.dict.keys():
			file.write("%s=%f\n"%(key,self.dict[key]))