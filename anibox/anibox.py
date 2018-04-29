import tkinter as tk
from PIL import Image, ImageTk
import time
import os

mpath = os.path.dirname(__file__)

class TilesetDimensionsError(Exception):
	def __init__(self, tileset):
		message = "This tileset is not formatted properly: %r" % tileset
		super(TilesetDimensionsError, self).__init__(message)

        
class Anibox(tk.Frame):
	def __init__(self, master, cnf={}, **kw):
		# Setup Anibox spefic attributes
		self.tile_dimensions = [36,36]
		self.placeholder = mpath + '\example2.png'
		sizemult = kw.pop('sizemult', 1)
		self.tileset = kw.pop('tileset', 'no image')
		self.tiles = self._getTiles(self.tileset, sizemult)
		self.speed = int(kw.pop('speed', 0.5) * 1000)
		self.updatetime = time.time()
		self.curindex = 0
		
		# container background
		tsbg = kw.pop('tbg', 'lightgrey') 
		
		# Call to Frame.__init__() must happen before creating container
		tk.Frame.__init__(self, master, cnf, **kw)
		self.container = tk.Label(self, image=self.tiles[0], border=0, bg=tsbg)
		self.container.pack()
		self.pos = self.getPos()
	
		# FPS tracking
		self.updatetime_prev = None
		
	def _getTiles(self, path, sizemult):
		tiles = []
		dimx = self.tile_dimensions[0] * sizemult
		dimy = self.tile_dimensions[1] * sizemult
		
		try:
			tileset = Image.open(path)
		except FileNotFoundError:
			path = self.placeholder
			tileset = Image.open(path)
		self.tileset = path
		
		w, h = tileset.size
		
		# Get number of tiles in set if tileset is formatted properly
		if h*sizemult == dimy and w*sizemult % dimx == 0:
			n = w*sizemult // dimx
		else:
			raise TilesetDimensionsError(tileset)
			
		tileset = tileset.resize((w*sizemult, h*sizemult))
		
		for i in range(n):
			x1 = i * dimx
			x2 = i * dimx + dimx
			tile = tileset.crop((x1, 0, x2, dimy))
			tiles.append(ImageTk.PhotoImage(tile))
		
		return tiles
	
	def resize(self, sizemult):
		self.tiles = self._getTiles(self.tileset, sizemult)
		self.container.config(image=self.tiles[0])
	
	def changespeed(self, speed):
		if speed < 0.001:
			return False
		self.speed = int(speed * 1000)
		print(self.speed)
		self.stop()
		self.start()
	
	def config(self, **kw):
		cbg = kw.pop('cbg', None)
		self.container.config(
			bg=cbg)
		tk.Frame.config(self, **kw)
	
	def getPos(self):
		x = self.container.winfo_x
		y = self.container.winfo_y
		return [x,y]
	
	def setBg(self, color):
		self.container.config(bg=color)
	
	def newTileset(self, path, **kw):
	
		speed = kw.pop('speed', self.speed)
		sizemult = kw.pop('sizemult', 1)
		self.tiles = self._getTiles(path, sizemult)
		self.container.config(image=self.tiles[0])
		self.speed = speed
	
	def update(self):
		self.updatetime_prev = self.updatetime
		self.updatetime = time.time()
		self.next()
		
	def next(self):
		length = len(self.tiles)
		i = self.curindex
		
		if i == length - 1:
			newpos = 0
		else:
			newpos = i + 1

		self.curindex = newpos
		self.container.config(image=self.tiles[newpos])
		
	def getFps(self):
		return 1 / self.speed
		
	def getRealFps(self):
		passed = self.updatetime - self.updatetime_prev
		
		if passed != 0:
			return round(1 / passed, 2)
		else:
			return 0

	def start(self):
		self.update()
		self.stop_id = self.after(self.speed, self.start)

	def stop(self):
		try:
			self.after_cancel(self.stop_id)
		except:
			print("Animation has not started!")
		
def main():		
	root = tk.Tk()
	ani = Anibox(root, tileset='example.png', speed=0.5, sizemult=10)
	ani.grid(column=0, row=0)
	ani.start()
	root.mainloop()
		
if __name__ == '__main__':
	main()
		