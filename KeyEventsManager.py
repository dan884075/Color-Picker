from os import name as osName

class WindowsKeyCodes:
	CTRL_CODE = 17
	C_CODE = 67
	V_CODE = 86

class LinuxKeyCodes:
	CTRL_CODE = 37
	C_CODE = 54
	V_CODE = 55


if osName == "nt":
	KEY_CODES = WindowsKeyCodes

elif osName == "posix":
	KEY_CODES = LinuxKeyCodes

else:
	raise ValueError("OS not supported")


class KeyEventsManager:
	
	def __init__(self, toBnd, copyFunc, pasteFunc):
		self.pressedKeys = set()
		self.copyFunc = copyFunc
		self.pasteFunc = pasteFunc
		
		toBnd.bind("<KeyPress>", self.__keyPressed)
		toBnd.bind("<KeyRelease>", self.__keyReleased)
		toBnd.bind("<Control-z>", lambda x: print("undo"))
		toBnd.bind("<Control-Z>", lambda x: print("redo"))
	
	
	def __keyPressed(self, event):
		curKeycode = event.keycode
		
		if not curKeycode in self.pressedKeys: #Ignore key already pressed keys
			self.pressedKeys.add(curKeycode)
			
			#If control is pressed ignore key events
			if not KEY_CODES.CTRL_CODE in self.pressedKeys:
				if curKeycode == KEY_CODES.C_CODE:
					self.copyFunc()
				
				elif curKeycode == KEY_CODES.V_CODE:
					self.pasteFunc()
	
	def __keyReleased(self, event):
		#A key can be released without being in pressedKeys
		#If is pressed with the window not focused or in a command with control
		self.pressedKeys.discard(event.keycode)