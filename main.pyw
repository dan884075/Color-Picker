from tkinter import Tk, Frame, Button, Checkbutton, BooleanVar, TclError, CENTER

from Color import validHTMLColor
from ColorSelector import ColorSelector
from KeyEventsManager import KeyEventsManager
from tkinterUtils import setWindowIcon, setWindowCenteredScreen, setWindowCenteredWindow


APP_ICON = "Degraded"

#Colors to show copy and paste actions in the entry with the HTML color
COPIED_COLOR = "#a5e2ff"
PASTED_COLOR = "#8aed91"
ERROR_COLOR = "#ef6464"

BUTTONS_FONT = "Calibri", 13

def createWindow(title, closeFunc):
	"""Creates a TopModeWindow with the aplication icon
	title: New window title
	closeFunc: Function to call on window close"""
	v = TopModeWindow()
	#v.overrideredirect(True)
	v.protocol("WM_DELETE_WINDOW", closeFunc)
	v.title(title)
	setWindowIcon(v, APP_ICON)
	
	return v


class TopModeWindow(Tk):
	"""Tkinter window that can be configured to be above the others, by pressing the 't' key"""
	
	def __init__(self, *args, changeCallback=None, **namedArgs):
		"""args: Positional arguments for tkinter window
		changeCallback: Funcion to be called when changed que top mode
		namedArgs: Named arguments for tkinter window"""
		super().__init__(*args, **namedArgs)
		
		self.changeCallback = changeCallback if changeCallback != None else lambda x: 0
		self.topMode = False
		self.bind("t", lambda event: self.__changeTopMode())
	
	
	def __changeTopMode(self):
		"""Changes the top mode"""
		self.topMode = not self.topMode
		self.attributes("-topmost", self.topMode)
		
		self.changeCallback(self.topMode)


class ColorWindow:
	"""Window to show a color
	The color is shown in the window background"""
	
	def __init__(self, mainWindow, closeFunc, color):
		"""mainWindow: Main window, is used to place this
		closeFunc: Function to call when the window is being closed.
			The object itself must be passed as a parameter. This function will call the close method
		
		color: Initial color to show"""
		self.colorWindow = createWindow("Color", lambda : closeFunc(self))
		setWindowCenteredWindow(self.colorWindow, mainWindow, (250, 250), alignRight=True)
		
		self.setBackground(color)
		
	def close(self):
		self.colorWindow.destroy()
	
	def setBackground(self, color):
		"""Changes the color
		color: New color to show"""
		self.colorWindow.config(bg=color)


class MainWindow:
	"""Manages the main window, with the color selector and the gui elements"""
	
	def __init__(self):
		self.txColorChanged = False
		self.auxWindows = []
		
		#Main window
		self.v = createWindow("Color Picker", self.close)
		setWindowCenteredScreen(self.v, (750, 500))
		
		self.keyEvents = KeyEventsManager(self.v, self.__copyColor, self.__pasteColor)
		self.v.bind("<Button-1>", self.__clicked)
		
		self.mainFrame = Frame(self.v)
		self.colorSelector = ColorSelector(self.mainFrame, self.setBackground)
		self.colorSelector.refreshColor()
		
		self.buttonsFrame = Frame(self.mainFrame)
		createBt = lambda command, text: Button(self.buttonsFrame, command=command, text=text, font=BUTTONS_FONT)
		
		self.btCopy = createBt(self.__copyColor, "Copy")
		self.btPaste = createBt(self.__pasteColor, "Paste")
		self.btAddSelector = createBt(self.colorSelector.addSelector, "Add selector")
		self.btDeleteSelector = createBt(self.colorSelector.deleteSelector, "Delete selector")
		self.btNewWindow = createBt(self.__newWindow, "New window")
		self.btCloseWindows = createBt(self.__closeAllAuxWindows, "Close all")
		self.btExit = createBt(self.close, "Exit")
		
		self.ckCopyHashVar = BooleanVar()
		self.ckCopyHashVar.set(True)
		self.ckCopyHash = Checkbutton(self.buttonsFrame, variable=self.ckCopyHashVar, text="Copy with #", font=BUTTONS_FONT)
		
		self.btCopy.grid(row=0, column=0, pady=(20, 5))
		self.btPaste.grid(row=1, column=0, pady=5)
		self.btAddSelector.grid(row=2, column=0, pady=(20, 5))
		self.btDeleteSelector.grid(row=3, column=0, pady=5)
		self.btNewWindow.grid(row=4, column=0, pady=(20, 5))
		self.btCloseWindows.grid(row=5, column=0, pady=5)
		self.btExit.grid(row=6, column=0, pady=(20, 5))
		self.ckCopyHash.grid(row=7, column=0, pady=5)
		
		self.colorSelector.getContainer().grid(row=0, column=0, padx=10)
		self.buttonsFrame.grid(row=0, column=1, padx=10, sticky="n")
		
		self.mainFrame.place(relx=0.5, rely=0.5, anchor=CENTER)


	def start(self):
		"""Starts the tkinter mainloop"""
		self.v.mainloop()
	
	def close(self):
		"""Destroys the main window, and all secondary windows contained"""
		self.v.update()
		self.__closeAllAuxWindows()
		
		self.btCopy.destroy()
		self.btPaste.destroy()
		self.btAddSelector.destroy()
		self.btDeleteSelector.destroy()
		self.btNewWindow.destroy()
		self.btCloseWindows.destroy()
		self.btExit.destroy()
		self.ckCopyHash.destroy()
		
		self.colorSelector.close()
		self.buttonsFrame.destroy()
		self.mainFrame.destroy()
		self.v.destroy()
	
	
	def __getCurHTMLColor(self):
		"""Returns the selected color in HTML format"""
		return self.colorSelector.getColor().getHTML()
	
	def setBackground(self):
		"""Updates the window background color with the new selected color
		Also updates all color windows"""
		newColor = self.__getCurHTMLColor()
		self.v.config(bg=newColor)
		
		for window in self.auxWindows:
			window.setBackground(newColor)
		
		if self.txColorChanged:
			self.__setBgHTMLColorEntry("white")
			self.txColorChanged = False
	
	def __setBgHTMLColorEntry(self, color):
		"""Changes the background color in all rgbTextSelectors
		color: New background color"""
		self.colorSelector.setTxEntriesColor(color)
	
	def __copyColor(self):
		"""Copies the selected color in the clipboard in HTML format"""
		htmlColor = self.__getCurHTMLColor()
		self.v.clipboard_clear()
		self.v.clipboard_append(htmlColor if self.ckCopyHashVar.get() else htmlColor[1:])
		
		self.__setBgHTMLColorEntry(COPIED_COLOR)
		self.txColorChanged = True
	
	def __pasteColor(self):
		"""Changes selected color with clipboard HTML color
		If the clipboard does not have a valid color shows an error in the rgbTextSelectors"""
		try:
			curClipboard = self.v.clipboard_get()
		
		except TclError:
			curClipboard = None
		
		if curClipboard != None and validHTMLColor(curClipboard):
			self.colorSelector.getColor().setFromHTML(curClipboard)
			self.colorSelector.refreshColor()
			newTxColor = PASTED_COLOR
		
		else:
			newTxColor = ERROR_COLOR
		
		self.__setBgHTMLColorEntry(newTxColor)
		self.txColorChanged = True
	
	def __newWindow(self):
		"""Creates a new ColorWindow to show the current color"""
		self.auxWindows.append(ColorWindow(self.v, self.__closeAuxWindow, self.__getCurHTMLColor()))
	
	def __closeAuxWindow(self, toRemove):
		"""Closes one secondary window, and removes it from the list of secondary windows
		toRemove: Secondary window to close"""
		toRemove.close()
		self.auxWindows.remove(toRemove)
	
	def __closeAllAuxWindows(self):
		"""Closes all secondary windows, and removes them from the list of secondary windows"""
		for window in self.auxWindows:
			window.close()
		
		self.auxWindows.clear()
	
	def __clicked(self, event):
		"""Runs on all clicks on the window
		If the clic is not in a text field focuses the main window"""
		if not event.widget in self.colorSelector.getEntries():
			self.v.focus()


def main():
	MainWindow().start()


if __name__ == '__main__':
	main()