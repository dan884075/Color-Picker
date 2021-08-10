from tkinter import Frame, Entry, Scale, HORIZONTAL, DoubleVar, StringVar
from tkinter.ttk import Combobox

from Color import Color, validHTMLColor, MIN_INT_BYTE, MAX_INT_BYTE


def addVarTrace(strVar, func):
	"""Adds a function to the write event of the StringVar
	strVar: StringVar to add the event
	func: Function to call in write events"""
	return strVar.trace_add("write", lambda name, index, mod: func())

def deleteVarTrace(strVar, idFunc):
	"""Removes the write event of the StringVar
	strVar: StringVar to remove the event
	idFunc: Event ID returned in addVarTrace"""
	strVar.trace_remove("write", idFunc)


class ComponentSelector:
	ENTRY_SIZE = 4
	SLIDER_SIZE = 400
	
	def __init__(self, master, changeColorCallback, rangeValues, sldColor="white"):
		"""Creates a selector for a color component
		master: Component to place the selector
		changeColorCallback: Callback to notify a color change
		rangeValues: Tuple with the values range to select. The limit values are included in the selection
		sldColor: Background color of the slider"""
		
		self.changeColorCallback = changeColorCallback
		self.rangeValues = rangeValues
		
		self.frame = Frame(master)
		
		self.strVar = StringVar()
		self.tx = Entry(self.frame, textvariable=self.strVar, width=ComponentSelector.ENTRY_SIZE)
		
		self.doubleVar = DoubleVar()
		self.sld = Scale(self.frame, from_=rangeValues[0], to=rangeValues[1],
			orient=HORIZONTAL, variable=self.doubleVar, command=self.__updateSlider,
			troughcolor=sldColor, length=ComponentSelector.SLIDER_SIZE)
		
		self.strVar.set("0")
		self.strVarTrace = addVarTrace(self.strVar, self.__updateTx)
		
		self.tx.grid(row=0, column=0, sticky="s")
		self.sld.grid(row=0, column=1)
	
	def getContainer(self):
		return self.frame
	
	def getEntry(self):
		return self.tx
	
	def close(self):
		self.sld.destroy()
		self.tx.destroy()
		self.frame.destroy()
	
	
	def __updateSlider(self, newVal):
		"""Runs when the slider is moved
		Updates the text field value and calls the change color callback
		newVal: New value of the slider"""
		self.__setTxVal(newVal)
		self.changeColorCallback()
	
	def __updateTx(self):
		"""Runs when the text field content changes, in a write event
		Updates the slider and calls the change color callback, only if the value in the text field is valid"""
		if self.__validNumber():
			self.doubleVar.set(int(self.tx.get()))
			self.changeColorCallback()
	
	def __setTxVal(self, newVal):
		"""Changes the text field value without generating a write event
		newVal: New value to set in the text field"""
		deleteVarTrace(self.strVar, self.strVarTrace)
		self.strVar.set(newVal)
		self.strVarTrace = addVarTrace(self.strVar, self.__updateTx)
	
	
	def setValue(self, value):
		"""Changes the selector value
		value: New selector value"""
		self.__setTxVal(str(value))
		self.doubleVar.set(value)
		
	def __validNumber(self):
		"""Returns whether the text field value is a valid number for the selector"""
		number = self.tx.get()
		
		if not number.isdigit():
			return False
		
		number = int(number)
		return number >= self.rangeValues[0] and number <= self.rangeValues[1]
	
	def getValue(self):
		"""Returns the selected value of the component"""
		return self.sld.get()


class Abstract_Selector:
	def __init__(self, color, updateFunc):
		self.setColor(color)
		self.updateFunc = updateFunc
	
	def setColor(self, color):
		self.color = color
	
	def changedColor(self):
		"""Called when this selector changes the color"""
		self.updateColor() #Update the Color object with the new represented color in this selector
		self.updateFunc() #Notify the color change


class AbstractComponentsSelector(Abstract_Selector):
	"""Abstract color selector with multiple component selectors"""
	
	def __init__(self, master, color, updateFunc):
		"""master: Component to place the color selector
		color: Color object with the current color
		updateFunc: Callback to notify color changes"""
		super().__init__(color, updateFunc)
		
		self.selectorFrame = Frame(master)
		self.selectors = self.createSelectors(self.selectorFrame)
		
		for i, selector in enumerate(self.selectors):
			selector.getContainer().grid(row=i, column=0)
	
	def close(self):
		for selector in self.selectors:
			selector.close()
		
		self.selectorFrame.destroy()
	
	def getContainer(self):
		return self.selectorFrame
	
	def getSelectors(self):
		"""Returns a tuple with all component selectors"""
		return self.selectors
	
	def getEntries(self):
		"""Returns al the text fields (Entry) in the selector"""
		return tuple(map(lambda x: x.getEntry(), self.selectors))


class RGB_Selector(AbstractComponentsSelector):
	
	def __init__(self, master, color, updateFunc):
		super().__init__(master, color, updateFunc)
	
	def createSelectors(self, master):
		"""Returns a tuple with all component selectors needed for the selector
		master: Component to place the selectors"""
		bytesInterval = (MIN_INT_BYTE, MAX_INT_BYTE)
		selectR = ComponentSelector(master, self.changedColor, bytesInterval, "red")
		selectG = ComponentSelector(master, self.changedColor, bytesInterval, "green")
		selectB = ComponentSelector(master, self.changedColor, bytesInterval, "blue")
		
		return selectR, selectG, selectB
	
	
	def updateColor(self):
		"""Updates the Color object with the new represented color in this selector"""
		self.color.setRGB(map(lambda x: x.getValue(), self.getSelectors()))
	
	def update(self):
		"""Updates the selectors to represent the color stored in the Color object after a color change"""
		for selector, val in zip(self.getSelectors(), self.color.getComponents()):
			selector.setValue(val)


class HSV_Selector(AbstractComponentsSelector):
	
	def __init__(self, master, color, updateFunc):
		super().__init__(master, color, updateFunc)
	
	def createSelectors(self, master):
		"""Returns a tuple with all component selectors needed for the selector
		master: Component to place the selectors"""
		hvsRange = (0, 1000)
		selectH = ComponentSelector(master, self.changedColor, hvsRange)
		selectS = ComponentSelector(master, self.changedColor, hvsRange)
		selectV = ComponentSelector(master, self.changedColor, hvsRange)
		
		return selectH, selectS, selectV
	
	
	def updateColor(self):
		"""Updates the Color object with the new represented color in this selector"""
		self.color.setFromHSV(*map(lambda x: x.getValue() / 1000, self.getSelectors()))
	
	def update(self):
		"""Updates the selectors to represent the color stored in the Color object after a color change"""
		for selector, val in zip(self.getSelectors(), self.color.getHSV()):
			selector.setValue(round(val * 1000))


class RGB_TextSelector(Abstract_Selector):
	FONT = "Consolas", 30
	
	def __init__(self, master, color, updateFunc):
		super().__init__(color, updateFunc)
		
		self.strVar = StringVar()
		self.txHTMLColor = Entry(master, width=7, font=RGB_TextSelector.FONT, textvariable=self.strVar)
		self.strVarTraceID = addVarTrace(self.strVar, self.__textChanged)
	
	def getContainer(self):
		return self.txHTMLColor
	
	def close(self):
		self.txHTMLColor.destroy()
	
	def getEntries(self):
		"""Returns a tuple with the selector text field"""
		return (self.txHTMLColor,)
	
	def setBgColor(self, color):
		"""Changes the background of the text field
		color: New background color to set"""
		self.txHTMLColor.config(bg=color)
	
	
	def __textChanged(self):
		"""Runs when the text field content changes, in a write event
		If the value in the text field is valid updates the color"""
		if validHTMLColor(self.txHTMLColor.get()):
			self.changedColor()
	
	def updateColor(self):
		"""Updates the Color object with the new represented color in this selector"""
		self.color.setFromHTML(self.txHTMLColor.get())
	
	def update(self):
		"""Updates the text field to represent the color stored in the Color object after a color change"""
		deleteVarTrace(self.strVar, self.strVarTraceID)
		self.strVar.set(self.color.getHTML())
		self.strVarTraceID = addVarTrace(self.strVar, self.__textChanged)


class ConfigurableSelector:
	"""Configurable selector with all selectors defined in SELECTORS dictionary
	The selector type can be changed with a combobox"""
	
	def __init__(self, master, initSelectorName, color, updateFunc, updateSelectorsFunc):
		"""master: Component to place the configurable color selector
		initSelectorName: Initial selector name
		color: Color object with the current color
		updateFunc: Callback to notify color changes
		updateSelectorsFunc: Callback to notify when the selector type is changed"""
		
		self.container = Frame(master)
		self.color = color
		self.updateFunc = updateFunc
		self.updateSelectorsFunc = updateSelectorsFunc
		
		self.selector = None
		
		self.selectorTypeCb = Combobox(self.container)
		self.selectorTypeCb["values"] = tuple(SELECTORS.keys())
		self.selectorTypeCb["state"] = "readonly"
		self.selectorTypeCb.set(initSelectorName)
		self.selectorTypeCb.bind("<<ComboboxSelected>>", self.__changeSelectorEvent)
		
		self.selectorTypeCb.grid(row=0, column=0, sticky="e")
		self.__changeSelector(initSelectorName)
	
	
	def close(self):
		self.selectorTypeCb.destroy()
		self.selector.close()
		self.container.destroy()
	
	def getContainer(self):
		return self.container
	
	def getSelector(self):
		"""Returns the selector"""
		return self.selector
	
	
	def __changeSelector(self, selectorName):
		"""Sets a new selector
		selectorName: New selector name"""
		self.selector = SELECTORS[selectorName](self.container, self.color, self.updateFunc)
		self.selector.getContainer().grid(row=1, column=0)
		self.selector.update()
	
	def __changeSelectorEvent(self, event):
		"""Called when the selector is changed in the combobox
		Destroys the old selector, creates a new one and calls the updateSelectorsFunc
		event: Combobox event"""
		self.selector.close()
		
		self.__changeSelector(self.selectorTypeCb.get())
		self.updateSelectorsFunc()


SELECTORS = {"RGB": RGB_Selector, "HSV": HSV_Selector, "HTML": RGB_TextSelector}
INIT_SELECTORS = ("RGB", "HSV", "HTML")


class ColorSelector:

	def __init__(self, master, updateColorFunc):
		"""master: Component to place the color selector
		updateColorFunc: Callback to notify color changes"""
		
		self.color = Color()
		self.updateColorFunc = updateColorFunc
		self.mainPannel = Frame(master)
		
		self.selectors = []
		for selectorName in INIT_SELECTORS:
			self.addSelector(selectorName)
		
		self.__updateSelectors()
	
	
	def getContainer(self):
		return self.mainPannel
	
	def close(self):
		for selector in self.selectors:
			selector.close()
		
		self.mainPannel.destroy()
	
	
	def refreshColor(self, skipSelector=-1):
		"""Updates the selectors to represent the new color and notifies the color change calling updateColorFunc
		skipSelector: Selector index to skip, in the case is already updated"""
		for i, selector in enumerate(self.selectors):
			if i != skipSelector:
				selector.getSelector().update()
		
		self.updateColorFunc()
	
	def getColor(self):
		"""Returns the Color object with the current color"""
		return self.color
	
	
	def addSelector(self, selectorName=INIT_SELECTORS[0]):
		"""Adds the specified selector to the color selector at the end
		selectorName: Selector name to add"""
		numSelector = len(self.selectors)
		
		selector = ConfigurableSelector(self.mainPannel, selectorName, self.color, lambda : self.refreshColor(numSelector), self.__updateSelectors)
		selector.getContainer().grid(row=numSelector, column=0, pady=(0, 15))
		self.selectors.append(selector)
	
	def deleteSelector(self):
		"""Deletes the last selector"""
		if len(self.selectors) > 0:
			self.selectors.pop(-1).close()
	
	def __updateSelectors(self):
		"""Called when some selector changes its type
		Updates the set with all text fields in the selectors
		Updates the list with all rgbTextSelectors"""
		
		self.selectorsEntries = set()
		for selector in self.selectors:
			self.selectorsEntries.update(selector.getSelector().getEntries())
			
		self.rgbTextSelectors = tuple(filter(lambda x: isinstance(x.getSelector(), RGB_TextSelector), self.selectors))
	
	def setTxEntriesColor(self, color):
		"""Changes the text fields background in all rgbTextSelectors
		color: New background color to set in the text fields"""
		for rgbTextSelector in self.rgbTextSelectors:
			rgbTextSelector.getSelector().setBgColor(color)
	
	def getEntries(self):
		"""Returns all text fields in the selector"""
		return self.selectorsEntries


def main():
	pass

if __name__ == '__main__':
	main()