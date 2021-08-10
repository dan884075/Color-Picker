from tkinter import Tk, Label, Button, Image
from os import name as osName

GEOMETRY_STR = "{}x{}+{}+{}"


def setWindowCenteredScreen(window, size):
		"""Cambia la geometria de la ventana indicada, con el tamaño indicado, y centrada en la ventana
		window: Ventana a configurar
		size: Tupla con el ancho in alto de la ventana en píxeles"""
		window.geometry(GEOMETRY_STR.format(*size, (window.winfo_screenwidth() // 2) - (size[0] // 2), (window.winfo_screenheight() // 2) - (size[1] // 2)))

def setWindowCenteredWindow(windowToCenter, baseWindow, newSize=None, alignRight=False, alignBottom=False):
	"""Centra la ventana indicada dentro de la ventana base
	windowToCenter: Ventana a centrar
	baseWindow: Ventana sobre la que se centrará
	newSize: Nuevo tamaño de la ventana centrada, si es None no se modifica"""
	toCenterSize = getWindowSize(windowToCenter) if newSize == None else newSize

	baseSize = getWindowSize(baseWindow)
	basePosition = getWindowPosition(baseWindow)
	
	xPos = basePosition[0] + (baseSize[0] if alignRight else (baseSize[0] // 2) - (toCenterSize[0] // 2))
	yPos = basePosition[1] + (baseSize[1] if alignBottom else (baseSize[1] // 2) - (toCenterSize[1] // 2))
	windowToCenter.geometry(GEOMETRY_STR.format(*toCenterSize, xPos, yPos))


def getWindowSize(window):
	"""Devuelve el tamaño de la ventana, (x, y)
	window: Ventan de la que se quiere el tamaño"""
	return window.winfo_width(), window.winfo_height()

def getWindowPosition(window):
	"""Devuelve una tupla con la posición de la ventana, (x, y)
	window: Ventana de la que se quiere la posición"""
	return window.winfo_x(), window.winfo_y()


def getFolderProgram():
	"""Devuelve la ruta del archivo actual"""
	path = __file__.replace("\\", "/")
	return path[:len(path) - path[::-1].index("/")]


def setWindowIcon(window, iconImage):
	"""Sets the icon of the window, to abstract the operation from the OS
	The icon file must be in the same folder than this file
	window: Window to set the icon
	iconImage: Filename of the icon to set, without extension
	If the os is windows the extension will be .ico, if the os is posix the extension will be .png"""
	
	if osName == "nt":
		window.iconbitmap(getFolderProgram() + iconImage + ".ico")

	elif osName == "posix":
		window.tk.call("wm", "iconphoto", window._w, Image("photo", master=window, file=getFolderProgram() + iconImage + ".png"))

	else:
		raise ValueError("OS not supported")


def main():
	pass

if __name__ == '__main__':
	main()