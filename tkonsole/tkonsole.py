import tkinter as tk
from inspect import signature


class TKonsole(tk.Frame):
	def __init__(self, master=None, cnf={}, **kw):
		cwidth = kw.pop('cwidth', 50)
		cheight = kw.pop('cheight', 10)
		cbc = kw.pop('cbc', False)

		tk.Frame.__init__(self, master, cnf, **kw)

		self.obox = OutputBox(self, cbc=cbc)
		self.obox.config(
			border=0,
			width=cwidth,
			height=cheight,
			bg='black',
			fg='white')			
		self.obox.pack(fill=tk.BOTH, expand=tk.YES)
		self.obox.pack_propagate(0)
		
		# Entry instead of text == equiv height to ibox
		self.prompt = tk.Entry(self)
		self.prompt.insert(tk.INSERT, '>')
		self.prompt.config(
			border=0,
			width=2,
			cursor='hand2',
			state=tk.DISABLED,
			disabledbackground='black',
			disabledforeground='white')
		self.prompt.pack(side='left')
		
		self.ibox = InputBox(self, obox=self.obox)
		self.ibox.config(
			border=0,
			width=cwidth,
			bg='black',
			fg='white',
			insertbackground='white')
		self.ibox.pack(side='left', fill='x', expand=True)
		
		# Optional 'click' input method
		self.prompt.bind('<Button-1>', self.ibox.addInput)
		
	def getInput(self):
		return self.ibox.getInput()
		
	def isCommand(self, s):
		splt = s.split()
		if not isinstance(splt, list):
			if splt in self.cmds:
				return True
		else:
			if splt[0] in self.cmds:
				return True
		
		return False
		
	def addOutput(self, s):
		self.obox.addOutput(s)
		
		
class InputBox(tk.Entry):
	def __init__(self, master=None, cnf={}, **kw):
		self.obox = kw.pop('obox', None)
		
		tk.Entry.__init__(self, master, cnf, **kw)
		self.bind('<Return>', self.addInput)
		self.bind('<Up>', self.histUp)
		self.bind('<Down>', self.histDown)
			
		self.queue = []
		self.curinput = False
		self.history = []
		self.history_index = 0

	def set(self, s):
		self.delete(0,'end')
		self.insert(0, s)
	
	# History logic could be cleaner, but it works ( was tired )
	def histUp(self, event):
		if self.history_index != 0:
			self.history_index -= 1
		if len(self.history) != 0:
			self.setHistory()
	
	def histDown(self, event):
		if self.history_index + 1 == len(self.history):
			self.set('')
			self.history_index += 1
			return False
		if self.history_index < len(self.history) - 1:
			self.history_index += 1
		if len(self.history) != 0 and self.history_index < len(self.history):
			self.setHistory()
	
	def setHistory(self):
		self.set(self.history[self.history_index])
	
	def addInput(self, event):
		line = self.get()
		if line == '':
			return False
		
		self.history.append(line)
		self.history_index = len(self.history)
		self.queue.append(line.strip())
		if self.obox is not None:
			self.obox.addOutput('>> ' + line)
		self.set('')
		
	def getInput(self):
		try:
			return self.queue.pop(0)
		except:
			return False

			
class OutputBox(tk.Text):
	def __init__(self, master=None, cnf={}, **kw):
		self.cbc = kw.pop('cbc', False)
		tk.Text.__init__(self, master, cnf, **kw)
		self.config(state=tk.DISABLED, cursor='arrow', wrap='char', 
        background='black',
        foreground='#7fff51',
        font='monaco 9')
		self.queue = []
		
		if self.cbc:
			self.cbcOutput()
		else:
			self.output()
		
	def addOutput(self, s):
		s = str(s)
		self.queue.append(s+'\n')
		
	def output(self):
		if len(self.queue) != 0:
			self.config(state=tk.NORMAL)
			self.insert(tk.END, self.queue.pop(0))
			self.config(state=tk.DISABLED)
			self.see('end')
			
		self.stop_id = self.after(25, self.output)
	
	def cbcOutput(self):
		# Output a line char by char
		if len(self.queue) != 0:
			self.see('end') #<- Do first; if last, moves down after line 
							# finished. This should be less awkward.
			line = self.queue[0]
			char = line[0]
			self.config(state=tk.NORMAL)
			self.insert(tk.END, char)
			self.config(state=tk.DISABLED)
			newline = line[1:len(line)]
			self.queue[0] = newline
		
			if len(self.queue[0]) == 0:
				self.config(state=tk.NORMAL)
				self.config(state=tk.DISABLED)
				self.queue.pop(0)
			
		self.stop_id = self.after(7, self.cbcOutput)
		
		
def main():
	root = tk.Tk()
	root.grid_columnconfigure(0, weight=15)
	root.grid_rowconfigure(3, weight=15)
	root.title('TKonsole Demo')
	
	try:
		root.iconbitmap(r'icon.ico')
	except:
		print('No icon.ico located!')
		
	root.config(bg='black')
	
	con1 = TKonsole(cwidth=50, cheight=10)
	con1.grid(column=0, row=2, stick=tk.E+tk.W)
	con2 = TKonsole(cwidth=1, cheight=1)
	con2.grid(column=0,row=3, stick=tk.E+tk.W+tk.S+tk.N)
	
	out1 = OutputBox(width=20, height=23)
	out1.config(border=0, bg='green', fg='white')
	out1.grid(column=2, row=2, rowspan=2, stick=tk.N+tk.S)
	
	label = tk.Label(root, text='TKonsole Demo')
	label.config(bg='black', fg='white')
	label.grid(column=0, row=0)
	
	split1 = tk.Frame(root, width=5, bg='green')
	split1.grid(column=1, row=2, rowspan=2, stick=tk.N + tk.S)
	
	split2 = tk.Frame(root, height=5, bg='green')
	split2.grid(column=0, row=1, columnspan=3, stick=tk.W + tk.E)
	
	while True:
		root.update()
			
		a = con1.getInput()
		b = con2.getInput()
		if a:
			con1.output(a)
			out1.output('> ' + a)
		if b:
			con2.output(b)
			out1.output('> ' + b) 
		
if __name__ == '__main__':
	main()