from re import fullmatch, compile as re_compile

RE_HTML_COLOR = re_compile("#[0-9a-fA-f]{6}")
HTML_COLOR_INITIAL = "#"
MAX_INT_BYTE = 0xff
MIN_INT_BYTE = 0x0

class InvalidColor(Exception):
	pass

class Color:
	"""Represents a 32bit RGB color
	It has no alpha"""
	
	def __init__(self, r=0, g=0, b=0):
		self.components = r, g, b
	
	def setRGB(self, components):
		"""Changes the color
		components: Iterable with new RGB components, in the range [0 - 255]"""
		self.components = tuple(components)
	
	def getComponents(self):
		"""Returns the current RGB components, in the range [0 - 255]"""
		return self.components
	
	def copy(self):
		"""Returns a copy of the current color"""
		color = Color()
		color.setRGB(self.components)
		return color
	
	def __repr__(self):
		return "r: {}, g: {}, b: {}".format(*self.components)
	
	def __toHex(self, number):
		"""Returns the two digits hexadecimal representation of the given number
		number: Number to get in hexadecimal, must be in range [0-255]"""
		if number < MIN_INT_BYTE or number > MAX_INT_BYTE:
			raise ValueError("Número fuera de rango")
		
		number = hex(number)[2:]
		return number if len(number) >= 2 else "0" + number
	
	def getHTML(self):
		"""Returns the HTML code associated to the current color"""
		return HTML_COLOR_INITIAL + "".join(map(self.__toHex, self.components))
	
	
	def setFromHTML(self, htmlText):
		"""Sets the given HTML color
		htmlText: HTML code of the new color"""
		if not validHTMLColor(htmlText):
			raise InvalidColor()
		
		self.setRGB((int(htmlText[i:i + 2], 16) for i in range(1, len(htmlText), 2)))
	
	
	def setFromHSV(self, h, s, v):
		"""Changes the color, given a representation in HSV
		h: Hue
		s: Saturation
		v: Value"""
		h = round(h * 1530)
		s_1 = 1 - s
		
		pos = (h // 510) % 3
		value = h % 510
		
		color = [0] * 3
		#Apply Hue
		color[pos] = MAX_INT_BYTE if value <= MAX_INT_BYTE else 510 - value
		color[(pos + 1) % 3] = value if value < MAX_INT_BYTE else MAX_INT_BYTE
		maxComp = max(color)
		
		#Apply Saturation
		for i in range(len(color)):
			if color[i] != maxComp:
				color[i] += (MAX_INT_BYTE - color[i]) * s_1
		
		#Apply Value
		for i in range(len(color)):
			color[i] *= v
		
		self.setRGB(map(round, color))
	
	def getHSV(self):
		"""Returns HSV representation of the current color"""
		color = list(self.components)
		v = max(color) / MAX_INT_BYTE #Compute Value
		
		if v == 0:
			return 0, 0, 0
		
		#Reverse Value modification
		for i in range(len(color)):
			color[i] /= v
		
		s_1 = min(color) / MAX_INT_BYTE #Compute (1 - Saturation)
		s = 1 - s_1 #Compute real Saturation
		if s < 1e-8:
			return 0, 0, v
		
		#Reverse Saturation modification
		for i in range(len(color)):
			color[i] = (color[i] - MAX_INT_BYTE * s_1) / s
		
		#Compute Hue
		posMax = tuple(map(round, color)).index(MAX_INT_BYTE) #Get the max component as reference
		val = 510 * posMax + (color[(posMax + 1) % 3] if color[posMax - 1] == 0 else -color[posMax - 1])
		h = (val % 1530) / 1530
		return h, s, v

def validHTMLColor(htmlText):
	"""Returns whether the String is a valid HTML color
	htmlText: Text with qthe color to check"""
	return fullmatch(RE_HTML_COLOR, htmlText) != None


def main():
	pass

if __name__ == '__main__':
	main()