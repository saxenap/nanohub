import random

class ContrastingColors:

	def __init__(self, bgcolor):
		self._usedColors = {}
		self._nextColorToUse = 0
		self._requestedColorCount = 0
		self._bgcolor = bgcolor
		if bgcolor == (0,0,0):
			self.contrastingColors = self.contrastingColorsBlack
			self.lowerRGB = 400
			self.upperRGB = 255*3 + 1
			self.dummyColor = (150, 150, 150)
		else:
			self.contrastingColors = self.contrastingColorsWhite
			self.lowerRGB = 150
			self.upperRGB = 300
			self.dummyColor = (150, 150, 150)
		
	contrastingColorsWhite = [
	(255,73,0),
	(255,0,0),
	(86,0,255),
	(0,43,255),
	(0,139,255)
	]
	contrastingColorsBlack = [
	(0,255,0),
	(223,255,0),
	(255,221,0),
	(255,147,0),
	(255,73,0),
	(255,0,0),
	(255,0,140),
	(178,0,255),
	(86,0,255),
	(0,43,255),
	(0,139,255),
	(0,234,255),
	(0,255,169)
	]
	
	def getRandomNewColor(self):
		r = 0
		g = 0
		b = 0
		while r + g + b > self.upperRGB or r + g + b < self.lowerRGB:
			r = random.randint(0, 255)
			g = random.randint(0, 255)
			b = random.randint(0, 255)
		return (r,g,b)
	
	def getContrastingColor(self, item):
		if item == 'dummy': return self.dummyColor
		elif item not in self._usedColors:
			self._usedColors[item] = self.contrastingColors[self._nextColorToUse]
			self._requestedColorCount += 1
			if self._nextColorToUse == len(self.contrastingColors) - 1:
				self.contrastingColors.append(self.getRandomNewColor())
			self._nextColorToUse += 1
			if self._requestedColorCount > self._nextColorToUse:
				print "Requested ", self._requestedColorCount, " colors for item ",item,", had only ", self._nextColorToUse + 1
		return self._usedColors[item]
		
	
	def getContrastingColors(self, items):
		rv = []
		for item in items:
			rv.append(self.getContrastingColor(item))
		return rv
