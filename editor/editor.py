import os
import sys
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox

# Global directories
project_path = os.path.dirname(os.path.realpath(__file__)) + '\\' + os.pardir
sys.path.append(project_path)
data_path = project_path + '/data' 

# Only importable if project directory is part of sys path
from general import peel, isIn, isNum, toNum
from tkonsole.tkonsole import OutputBox
from datparser import DatParser
    
class Field(tk.Frame):
    """A Base field class intended to be sub-classed"""
    
    def __init__(self, master=None, cnf={}, **kw):
        self.master = master
        self.value_name = kw.pop('value_name', 'grnc')
        self.g_type = kw.pop('g_type', 'universal')
        self.g_subtype = kw.pop('g_subtype', 'general')
        tk.Frame.__init__(self, master, cnf, **kw)
        self.grid_columnconfigure(1, weight=15)
        
        self.label = tk.Label(self, text=self.value_name.title(), width=8)
        self.label.grid(row=0, column=0, stick='w')
        
        self.config(highlightthickness=1, highlightbackground='grey')
        
    def set(self, s=''):
        """Implement me in subclass"""
        
        pass
        
    def getValue(self):
        """Implement me in subclass"""
        
        pass
        
    def getName(self):
        return self.value_name.lower()
        
        
class EntryField(Field):
    """An entry field is a Field that only deals with a tk.Entry object.
    It's essentially just a tk.Entry with some specific functionality both
    specifically defined in the class as well inheristed from the base Field
    class."""
    
    def __init__(self, master=None, cnf={}, **kw):
        text = kw.pop('text', '')
        width = kw.pop('width', 50)
        Field.__init__(self, master, cnf, **kw)
        self.entry = tk.Entry(self, width=width, text=text)
        self.entry.grid(row=0, column=1, stick='ew')

    def set(self, s):
        """Set the text inside the EntryField's associated tk.Entry to
        the value of the arg s supplied as an argument."""
        
        self.entry.delete('0', 'end')
        if isinstance(s, list):
            s = "%s" % ', '.join(map(str, s))
        self.entry.insert(0, s)
        
    def getValue(self):
        """Retrive the string within the associated tk.Entry."""
        
        return self.entry.get()
    
    
class TextField(Field):
    """A Field that has a tk.Text as the associated textual i/o widget."""
    
    def __init__(self, master=None, cnf={}, **kw):
        text = kw.pop('text', '')
        width = kw.pop('width', 50)
        Field.__init__(self, master, cnf, **kw)
        self.text = tk.Text(self, width=width, height=6, wrap='word')
        self.text.insert('insert', text)
        self.text.grid(row=0, column=1, stick='ew')
        
    def set(self, s):
        """Set the value within the associated tk.Text widget to arg s"""
        
        self.text.delete('0.0','end')
        self.text.insert('0.0', s)
        
    def getValue(self):
        """Get the value from the associated tk.Text."""
        
        return self.text.get('0.0', 'end')
        

class ListField(Field):
    """A Field that includes a ListWindow and a tk.Entry. The ListWindow
    holds a list of fields that get appended to a string in the guise of a
    python list. This stringy list get set into the associate tk.Entry."""
    
    def __init__(self, master=None, cnf={}, **kw):
        self.datpaths = kw.pop('datpaths', [])
        self.valid_fields = kw.pop('valid_fields', ['field'])
        self.valid_selections = kw.pop('valid_selections', [])
        self.locked = kw.pop('locked', False)
        text = kw.pop('text', '')
        width = kw.pop('width', 50)
        
        Field.__init__(self, master, cnf, **kw)
        self.lw = None
        self.entry = tk.Entry(self, width=width, text=text)
        self.entry.insert(0, '[]')
        self.entry.config(state='disabled')
        self.entry.grid(row=0, column=1, stick='ew')
        self.btn_openlw = tk.Button(self, text='+', command=self.openlw)
        self.btn_openlw.grid(row=0, column=2)
        self.parser = DatParser()
            
    def _populate(self):
        """A helper method that puplates the associated ListWindow with values
        from the string currently held within the associated tk.Entry."""
        
        s = self.entry.get()
        value = self.parser.valFromStr(s)
        
        # Make sure value is of list type
        if not isinstance(value, list):
            value = '[' + str(value).strip() + ']'
            value = self.parser.valFromStr(value)
            
        for item in value:
            if not item == '':
                self.lw.append(str(item))
        
    def closelw(self):
        """Close the associated ListWindow if open."""
        
        if self.lw != None:
            self.lw._onclose()
            self.lw = None
        
    def openlw(self):
        """Open and pupulate new List window, assigning it to self.lw"""
        
        x = self.master.winfo_rootx() + self.master.winfo_width()
        y = self.master.winfo_rooty()
        if self.lw != None:
            self.lw.destroy()
            
        self.lw = ListWindow(
            locked=self.locked, 
            title=self.value_name,
            datpaths=self.datpaths,
            valid_fields=self.valid_fields,
            valid_selections=self.valid_selections)
            
        self.lw.geometry('+%d+%d' % (x, y))
        self.lw.attributes('-topmost', True)
        self.lw.connect(self.entry)
        self.lw.protocol('WM_DELETE_WINDOW', self.closelw)
        self._populate()
        self.lw.pollSet()
        
    def set(self, x):
        """Set the value of the associated tk.Entry to the value of x."""
        
        self.entry.config(state='normal')
        self.entry.delete('0', 'end')
        self.entry.config(state='disabled')
        if isinstance(x, list):
            x = '[' + "%s" % ', '.join(map(str, x)) + ']'
        self.entry.config(state='normal')
        self.entry.insert(0,x)
        self.entry.config(state='disabled')
    
    def getValue(self):
        """Return the value from the associate tk.Entry"""
        
        return self.entry.get()
        

class MapField(Field):
    """Like a listfield, but for working with maps."""
    def __init__(self, master=None, cnf={}, **kw):
        self.datpaths = kw.pop('datpaths', [])
        Field.__init__(self,master, cnf, **kw)
        self.label = tk.Label(self, text=self.value_name.title())
        self.label.grid(row=0, column=0)
        self.entry = tk.Entry(self)
        self.entry.grid(row=0, column=1, stick='ew')
        self.btn_open_rm = tk.Button(self, text='M', command=self.open_rm)
        self.btn_open_rm.grid(row=0, column=2)
        self.rm = None
        
    def open_rm(self):
        self.rm = RoomMapper(self)
        
        
class RoomMapper(tk.Toplevel):

    def __init__(self, master=None, cnf={}, **kw):
        title = kw.pop('title', 'List Window')
        self.grid_size = kw.pop('grid_size', 50)
        self.datpaths = kw.pop('datpaths', [])
        tk.Toplevel.__init__(self, master, cnf, **kw)
        self.config(background='black')
        self.title('Room Mapper')
        self.geometry('800x800')
        self.connected = None
        self.bpoints = []
        self.gridlines = []
        canvas_width = 2000
        canvas_height = 2000
        self.zoom_step = canvas_width / self.grid_size
        self.canvas = tk.Canvas(self, width=canvas_width,
            height=canvas_height, highlightthickness=0, background='blue')
        self.width = self.canvas.winfo_reqwidth()
        self.height = self.canvas.winfo_reqheight()
        self.setBpoints(self.grid_size)
        self.boxes = []
        self.setGrid(self.grid_size)
        
        self.canvas_px = self.winfo_width() / 2
        self.canvas_py = self.winfo_height() / 2
        self.canvas.place(x=self.canvas_px, y=self.canvas_py)
        self.canvas.bind('<Configure>', self._on_configure)
        self.canvas.bind('<ButtonPress-1>', self._on_click)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<MouseWheel>', self._zoom)
        self.stopcode_move = None
        self.stopcode_checkMove = None
        self.mouse_position = self.getMousePos()
        
        self.selected_room = None
        
        # Room info panel
        self.grid_columnconfigure(1, weight=1)
        self.i_panel = tk.Frame(self)
        self.i_panel.grid(row=0, column=1, stick='en')
        self.i_room = SelectionField(
            self.i_panel,
            datpaths=[data_path + '\ROOMS.DAT'],
            value_name='Room',
            g_type='Room', g_subtype='Room'
            )
        self.i_room.grid(row=0, column=0)
        
        self.i_eNorth = SelectionField(
            self.i_panel,
            options=['No', 'Yes'],
            value_name='N exit')
        self.i_eNorth.grid(row=2, column=0)   
        
        self.i_eSouth = SelectionField(
            self.i_panel,
            options=['No', 'Yes'],
            value_name='S exit')
        self.i_eSouth.grid(row=3, column=0)  
        
        self.i_eEast = SelectionField(
            self.i_panel,
            options=['No', 'Yes'],
            value_name='E exit')
        self.i_eEast.grid(row=4, column=0)  
        
        self.i_eWest = SelectionField(
            self.i_panel,
            options=['No', 'Yes'],
            value_name='W exit')
        self.i_eWest.grid(row=5, column=0)  
        
        self.i_save = tk.Button(self.i_panel, text='Save', command=self.save_selected)
        self.i_save.grid(row=6, column=0)
        
        # stat Display
        self.s_panel = tk.Frame(self, bg='black')
        self.s_panel.grid(row=0, column=0, stick='w')
        
        self.text_gridsize_var = tk.StringVar()
        self.text_gridsize = tk.Label(self.s_panel, 
            textvariable=self.text_gridsize_var, bg='black', fg='white')
        self.text_gridsize.grid(row=0, column=0, stick='w') 
        
        self.text_boxCount_var = tk.StringVar()
        self.text_boxCount = tk.Label(self.s_panel,
            textvariable=self.text_boxCount_var, bg='black', fg='white')
        self.text_boxCount.grid(row=1, column=0, stick='w') 
        
        self.text_bPointCount_var = tk.StringVar()
        self.text_bPointCount = tk.Label(self.s_panel,
            textvariable=self.text_bPointCount_var, bg='black', fg='white')
        self.text_bPointCount.grid(row=2, column=0, stick='w')
        
        self.text_canvasDim_var = tk.StringVar()
        self.text_canvasDim = tk.Label(self.s_panel,
            textvariable=self.text_canvasDim_var, bg='black', fg='white')
        self.text_canvasDim.grid(row=3, column=0, stick='w')
        self._update_info()

        
    def _update_info(self):
        self.text_gridsize_var.set('Gridsize: %s' % self.grid_size)
        self.text_boxCount_var.set('Boxes: %s' % len(self.boxes))
        self.text_bPointCount_var.set('bPoints: %s' % len(self.bpoints))
        self.text_canvasDim_var.set('Canvas: x%s/y%s' % (self.width, self.height))
        
        self.after(350, self._update_info)
           
    def _zoom(self, event):
        step = self.zoom_step
        if event.delta < 0:
            direction = -1
        else:
            direction = 1
        
        new_grid_size = self.grid_size + direction
        
        new_width = step*2
        new_height = step*2
        
        if not new_grid_size <= 0:
            new_width = self.width + step * direction
            new_height = new_width
            self.grid_size = new_grid_size
            self.canvas.config(width=new_width, height=new_height)
        
    def _on_click(self, event=None):
        if self.stopcode_checkMove == None:
            self.mouse_position = self.getMousePos()
        x, y = self.getMousePos()
        dx = abs(x - self.mouse_position[0])
        dy = abs(y - self.mouse_position[1])
        
        # Check if enough distance made to iniitiate move
        if dx > 10 or dy > 10:
            self.after_cancel(self.stopcode_checkMove)
            self.config(cursor='none')
            self.stopcode_checkMove = None
            self.mouse_position = self.getMousePos()
            self._move(True)
        else:
            self.stopcode_checkMove = self.after(50, self._on_click)

    def _on_release(self,event):
        if self.stopcode_move:
            self.after_cancel(self.stopcode_move)
            self.stopcode_move = None
            self.config(cursor='arrow')
        else:
            self.select([event.x,event.y])
            
        if self.stopcode_checkMove != None:
            self.after_cancel(self.stopcode_checkMove)
            self.stopcode_checkMove = None

    def _move(self, drag=False, dx=None, dy=None):
        if dx == None or dy == None and drag == True:
            pos = self.getMousePos()
            dx = pos[0] - self.mouse_position[0]
            dy = pos[1] - self.mouse_position[1]
            self.mouse_position = pos
            
        self.canvas_px = self.canvas_px + dx
        self.canvas_py = self.canvas_py + dy
        self.canvas.place(x=self.canvas_px, y=self.canvas_py)
        if drag or self.stopcode_move:
            self.stopcode_move = self.after(10, self._move)
    
    def _on_configure(self, event):
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        if self.stopcode_move == None:
            self.setBpoints(self.grid_size)
            self.setGrid(self.grid_size)
            self.resize_boxes(self.grid_size)
    
    def resize_boxes(self, size):
        for roombox in self.boxes:
            for i in range(len(self.bpoints)):
                id = roombox.getID()
                if i == id:
                    bPoint = self.bpoints[i]
            roombox.setbPoint(bPoint)
            roombox.toTop()
     
    def setGrid(self, size):
        for line in self.gridlines:
            self.canvas.delete(line)
        del(self.gridlines)
        self.gridlines = []
        
        for x in range(self.width):
            if x % size == 0:
                line = self.canvas.create_line(x, 0, x, self.height)
                self.gridlines.append(line)
                
        for y in range(self.height):
            if y % size == 0:
                line = self.canvas.create_line(0, y, self.width, y)
                self.gridlines.append(line)
            
    def setBpoints(self, size):
        for bpoint in self.bpoints:
            self.canvas.delete(bpoint)
        del(self.bpoints)
        self.bpoints = []
        
        for x in range(self.width):
            if x % size == 0:
                for y in range(self.height):
                    if y % size == 0:
                        self.bpoints.append([x,y, x+size, y+size])
  
    def remove_unsaved(self):
        i = 0
        delete_these = []
        for box in self.boxes:
            if not box.isSaved():
                box.delete()
                delete_these.append(i)
            i += 1
            
        for d in delete_these:
            del(self.boxes[d])
                
    def save_selected(self):
        if self.selected_room != None:
            pass
        else:
            return None
        # Assign room gob to be associated with
        self.selected_room.setRoom(self.i_room.getValue())
        
        # Assign avaialble exits
        n = self.i_eNorth.getValue()
        s = self.i_eSouth.getValue()
        e = self.i_eEast.getValue()
        w = self.i_eWest.getValue()
        
        self.selected_room.setExits(n=n, s=s, e=e, w=w)
        self.selected_room.save()
    
    def load_selected(self):
        self.i_room.set(self.selected_room.getRoom())
        
        exits = self.selected_room.getExits()
        # Convert True/False to Yes/No
        for exit in exits:
            if exits[exit] == True:
                exits[exit] = 'Yes'
            elif exits[exit] == False:
                exits[exit] = 'No'
        
        self.i_eNorth.set(exits['north'])
        self.i_eSouth.set(exits['south'])
        self.i_eEast.set(exits['east'])
        self.i_eWest.set(exits['west'])

    def check_saved(self, id):
        for roombox in self.boxes:
            if roombox.getID() == id:
                return True
        return False
     
    def getRoomByID(self, id):
        for roombox in self.boxes:
            if roombox.getID() == id:
                return roombox
        return False
     
    def deselect_all(self):
        for roombox in self.boxes:
            roombox.deselect()
     
    def select(self, point):
            self.remove_unsaved()
            if self.selected_room != None:
                self.selected_room.deselect()
                
            selected = False
            id = 0
            for bpoint in self.bpoints:
                x, y, x2, y2 = bpoint[0], bpoint[1], bpoint[2], bpoint[3]
                if point[0] > x and point[0] <= x2:
                    if point[1] > y and point[1] <= y2:
                        selected = bpoint
                        break
                id += 1
            
            if selected:
                pass
            else:
                return False
                
            if self.check_saved(id):
                roombox = self.getRoomByID(id)
            else:
                roombox = RoomBox(self.canvas, selected, id, self.grid_size)
                self.boxes.append(roombox)
            
            roombox.select()
            self.selected_room = roombox
            self.load_selected()
     
    def getMousePos(self):
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        return [x, y]
        
    def connect(self, entry):
        self.connected = entry
        
        
class RoomBox(object):
    def __init__(self, canvas, bPoint, id, size=20, fill='blue', outline='red'):
        self.id = id
        self.canvas = canvas
        self.bPoint = bPoint
        self.size = size
        self.fill = fill
        self.outline = outline
        self.selected = False
        
        # Room attributes
        self.saved = False
        self.room = None
        self.exits = {
            'north':False,
            'south':False,
            'east':False,
            'west':False
            }
        
        # {map:entrance}
        self.map_exit = False
        
        # Walls
        x, y, x2, y2 = bPoint[0], bPoint[1], bPoint[2], bPoint[3]
        self.rec = canvas.create_rectangle(x+1, y+1, x2, y2, fill=fill, outline='')
        wNorth = self.canvas.create_rectangle(x+1, y+1, x2, y+3, fill=self.outline, outline='')
        wSouth = self.canvas.create_rectangle(x+1, y2, x2, y2-2, fill=self.outline, outline='')
        wEast = self.canvas.create_rectangle(x2, y+1, x2-2, y2, fill=self.outline, outline='')
        wWest = self.canvas.create_rectangle(x+1, y+1, x+3, y2, fill=self.outline, outline='')
        self.walls = {
            'north':wNorth,
            'south':wSouth,
            'east':wEast,
            'west':wWest
            }
        self.walls_fill = {
            'north':self.outline,
            'south':self.outline,
            'east':self.outline,
            'west':self.outline
            }
        
    def isSaved(self):
        return self.saved
        
    def getbPoint(self):
        return self.bPoint
    
    def getID(self):
        return self.id
    
    def getSize(self):
        return self.size
    
    def getRoom(self):
        return self.room
    
    def getExits(self):
        return self.exits
    
    def setFill(self, color):
        self.canvas.itemconfig(self.rec, fill=color)
        
    def setOutline(self, color):
        self.canvas.itemconfig(self.rec, outline=color)
  
    def setWallFill(self, **kw):
        for key in kw:
            fill = kw[key]
            if key == 'n':
                wall = self.walls['north']
                self.walls_fill['north'] = fill
                self.canvas.itemconfig(wall, fill=fill)
            if key == 's':
                wall = self.walls['south']
                self.walls_fill['south'] = fill
                self.canvas.itemconfig(wall, fill=fill)
            if key == 'e':
                wall = self.walls['east']
                self.walls_fill['east'] = fill
                self.canvas.itemconfig(wall, fill=fill)
            if key == 'w':
                wall = self.walls['west']
                self.walls_fill['west'] = fill
                self.canvas.itemconfig(wall, fill=fill)
                
    def setSize(self, size):
        # walls
        for key in self.walls:
            print('HERE')
            wall = self.walls[key]
            bPoint = self.canvas.coords[wall]
            bPoint[2] += size
            bPoint[3] += size
            self.canvas.coords(wall, *bPoint)
        # rec  
        bPoint = self.canvas.coords(self.rec)
        bPoint[0] += size
        bPoint[1] += size
        self.canvas.coords(self.rec, *bPoint)
    
    def setExits(self, **kw):
        if 'n' in kw:
            wall = self.walls['north']
            if kw['n'] == 'Yes':
                self.exits['north'] = True
                self.setWallFill(n='lightgreen')
            elif kw['n'] == 'No':
                self.exits['south'] = False
                self.setWallFill(n=self.outline)
        if 's' in kw:
            wall = self.walls['south']
            if kw['s'] == 'Yes':
                self.setWallFill(s='lightgreen')
                self.exits['south'] = True
            elif kw['s'] == 'No':
                self.setWallFill(s=self.outline)
                self.exits['south'] = False
        if 'e' in kw:
            wall = self.walls['east']
            if kw['e'] == 'Yes':
                self.setWallFill(e='lightgreen')
                self.exits['east'] = True
            elif kw['e'] == 'No':
                self.setWallFill(e=self.outline)
                self.exits['east'] = False
        if 'w' in kw:
            wall = self.walls['west']
            if kw['w'] == 'Yes':
                self.setWallFill(w='lightgreen')
                self.exits['west'] = True
            elif kw['w'] == 'No':
                self.setWallFill(w=self.outline)
                self.exits['west'] = False
                 
    def move(self, dx, dy):
        self.canvas.move(self.rec, dx, dy)
        
    def select(self):
        for key in self.walls:
            wall = self.walls[key]
            self.canvas.itemconfig(wall, fill='white')
        self.canvas.itemconfig(self.rec, fill=self.fill)
        self.selected = True
    
    def deselect(self):
        nFill = self.walls_fill['north']
        sFill = self.walls_fill['south']
        eFill = self.walls_fill['east']
        wFill = self.walls_fill['west']
        self.setWallFill(n=nFill, s=sFill, e=eFill, w=wFill)
        self.canvas.itemconfig(self.rec, fill=self.fill)
        self.selected = False
        
    def setbPoint(self, bPoint):
        self.bPoint = bPoint
        x, y, x2, y2 = bPoint[0], bPoint[1], bPoint[2], bPoint[3]
        #rec
        self.canvas.coords(self.rec, x+1, y+1, x2, y2)
        # walls
        bNorth = [x+1, y+1, x2, y+3]
        bSouth = [x+1, y2, x2, y2-2]
        bEast = [x2, y+1, x2-2, y2]
        bWest = [x+1, y+1, x+3, y2]
        self.canvas.coords(self.walls['north'], *bNorth)
        self.canvas.coords(self.walls['south'], *bSouth)
        self.canvas.coords(self.walls['east'], *bEast)
        self.canvas.coords(self.walls['west'], *bWest)
        
    def setRoom(self, room):
        self.room = room
        
    def redraw(self):
        self.canvas.delete(self.rec)
        self.canvas.create_rectangle(self.bPoint, 
            fill=self.fill, outline=self.outline)
    
    def toTop(self):
        self.canvas.tag_raise(self.rec)
        for key in self.walls:
            wall = self.walls[key]
            self.canvas.tag_raise(wall)
    
    def save(self):
        self.saved = True
        self.fill = 'darkblue'
        self.outline = 'red'
        self.canvas.itemconfig(self.rec, fill=self.fill)
        nFill = self.walls_fill['north']
        sFill = self.walls_fill['south']
        eFill = self.walls_fill['east']
        wFill = self.walls_fill['west']
        self.setWallFill(
            n=nFill, 
            s=sFill, 
            e=eFill, 
            w=wFill)
        self.select()
    
    def unsave(self):
        self.saved = False
        
    def delete(self):
        self.canvas.delete(self.rec)
        for key in self.walls:
            self.canvas.delete(self.walls[key])
  
class SelectionField(Field):
    """A Field that has a tk.OptionMenu. Options will be appended to the
    tk.OptionMenu from the names of GOBs contained in the given .DATs read from
    locations provided in self.datpaths. Options can also be manually added via
    self.add_option(label)."""
    
    def __init__(self, master=None, cnf={}, **kw):
        omwidth = kw.pop('omwidth', 10)
        omheight = kw.pop('omheight', 1)
        OPTIONS = kw.pop('options', ['None'])
        datpaths = kw.pop('datpaths', [])
        valid_selections = kw.pop('valid_selections', [])

        parser = DatParser()
        parser.read(*datpaths)
        for gob in parser.getGobs():
            if len(valid_selections) != 0:
                if not gob.getAttr('subtype') in valid_selections:
                    continue
            OPTIONS.append(gob.getAttr('name'))
            
        Field.__init__(self, master, cnf, **kw)
        self.om_VAR = tk.StringVar(self)
        self.om_VAR.set(OPTIONS[0])
        self.om = tk.OptionMenu(self, self.om_VAR, *OPTIONS)
        self.om.config(width=omwidth, height=omheight)
        self.om.grid(row=0, column=1, stick='ew')
        
    def add_option(self, label=''):
        """Add an option to the associated tk.OptionMenu."""
        
        self.om['menu'].add_command(
                label=label,
                command=tk._setit(self.om_VAR,
                label))
                
    def delete_options(self):
        m = self.om['menu']
        m.delete(0,'end')
        
    def new_options(self, options):
        self.delete_options()
        for option in options:
            self.om['menu'].add_command(
                label=labal,
                command=tk._setit(self.om_VAR,
                label))
        
    def getValue(self):
        """Get the value of the currently selected option in the associated
        tk.OptionMenu."""
        
        return self.om_VAR.get()
        
    def set(self, s):
        """Set the currently selected option in the associated tk.OptionMenu to
        value of arg s"""
        
        self.om_VAR.set(s)
       
       
class CompoundField(Field):
    """A Field with two parts that when calling its getValue() method returns a value
    comprised of both part's contained values. Part one is a SelectionField and
    part 2 is a tk.Text.
    eg:
    self.sf.getValue() -> 'Hello '
    self.text.get(0.0, 'end') -> 'World!'
    
    then
    
    self.getValue() -> 'Hello World!'
    """
    
    def __init__(self, master=None, cnf={}, **kw):
        OPTIONS = kw.pop('options', ['None'])
        OPTIONS_secondary = kw.pop('options_secondary', ['None'])
        val = kw.pop('val', False)
        self.datpaths = kw.pop('datpaths', [])
        self.datpaths_secondary = kw.pop('datpaths_secondary', [])
        
        self.sepchar = kw.pop('sepchar', '|+|')
        fieldstr_a = kw.pop('field_a', 'entry')
        fieldstr_b = kw.pop('field_b', 'entry')
        
        valid_selections = kw.pop('valid_selections', [])
        
        Field.__init__(self, master, cnf, **kw)
           
        if fieldstr_a == 'entry':
            self.fa = EntryField(self)
        elif fieldstr_a == 'text':
            self.fa = TextField(self)
        elif fieldstr_a == 'selection':
            self.fa = SelectionField(self, datpaths=self.datpaths, options = OPTIONS)
            
        if fieldstr_b == 'entry':
            self.fb = EntryField(self)
        elif fieldstr_b == 'text':
            self.fb = TextField(self)
        elif fieldstr_b == 'selection':
            self.fb = SelectionField(self, datpaths=self.datpaths_secondary, options = OPTIONS_secondary)
        
        if val:
            vals = val.split(self.sepchar)
            assert len(vals) == 2
                
            val_a = vals[0]
            val_b = vals[1]
            self.fa.set(val_a)
            self.fb.set(val_b)
        self.fa.grid(row=0, column=0)
        self.fb.grid(row=0, column=1)

        
    def getValue(self):
        return self.fa.getValue() + self.sepchar + self.fb.getValue()
        
    def update_options(self, options):
        if isinstance(self.fa, SelectionField):
            self.fa.new_options(options)
    
    def update_options_secondary(self, options):
        if isinstance(self.fb, SelectionField):
            self.fb.new_options(options)

        
class ListWindow(tk.Toplevel):
    """A tk.Toplevel window that includes a list of values
    cooresponding to a connected tk.Entry or tk.Text. Values should be able
    to be recieved from an textual widget as well as set the entry to the values
    presented in the ListWindow."""
    
    def __init__(self, master=None, cnf={}, **kw):
        title = kw.pop('title', 'List Window')
        locked = kw.pop('locked', False)
        self.datpaths = kw.pop('datpaths', [])
        self.datpaths_secondary = kw.pop('datpaths_secondary', [])
        self.valid_fields = kw.pop('valid_fields', ['field'])
        self.valid_selections = kw.pop('valid_selections', [])
        tk.Toplevel.__init__(self, master, cnf, **kw)
        self.title(title)
        self.protocol('WM_DELETE_WINDOW', self._onclose)
        self.textual = None
        self.fields = []
        
        # Create canvas for scrolling through appended fields
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.canvas.grid(row=0, column=0, stick='ewns')
        self.vsb = tk.Scrollbar(self, orient='vertical',
            command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, stick='nse')
        self.canvas.config(yscrollcommand=self.vsb.set)
        self.widget_cont = tk.Frame(self.canvas)
        self.widget_cont.pack(fill='both')
        self.canvas.create_window((0,0), window=self.widget_cont, anchor="nw",
            tags="self.widget_cont")
        
        self.widget_cont.bind("<Configure>", self._onFrameConfigure)
        self.wcheight = self.widget_cont.winfo_reqheight()
        
        # If locked, don't provide an append button
        if not locked:
            self.appender = self._createAppender()
            
        self.stopcode_set = 0
    
    def _onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.config(scrollregion=self.canvas.bbox("all"),
            width=self.widget_cont.winfo_reqwidth())
        height = self.widget_cont.winfo_reqheight()
        
        # Move yview to bottom of canvas when height of widget_cont changes
        if height != self.wcheight:
            self.canvas.yview_moveto(1)
            self.wcheight = height
        
    def _createAppender(self):
        """Create a button that will function as a way to append new
        fields to the ListWindow. This button will drop down a list of valid
        Fields that can be added. Upon slection, the Field chosen will be added
        via the appropriate method based on the type of Field selected. The
        appender will then be moved down for future appendings."""
        
        n = len(self.fields)
        frame = tk.Frame(self.widget_cont)
        frame.grid(row=n, column=0, stick='we', columnspan=2)
        frame.grid_columnconfigure(0, weight=1)
        btnmenu = ButtonMenu(frame, text='+')

        if 'entry' in self.valid_fields or 'field' in self.valid_fields:
            btnmenu.add_command(label='Entry', command=self.addEntry)
            
        if 'text' in self.valid_fields or 'field' in self.valid_fields:
            btnmenu.add_command(label='Text', command=self.addText)
            
        if 'selection'in self.valid_fields or 'field' in self.valid_fields:
            btnmenu.add_command(label='Selection', command=self.addSelection)
            
        if 'compound' in self.valid_fields or 'field' in self.valid_fields:
            btnmenu.add_command(label='Compound', command=self.addCompound)
            
        if 'convo' in self.valid_fields or 'field' in self.valid_fields:
            btnmenu.add_command(label='Convobit', command=self.addConvobit)
            
        btnmenu.grid(row=0, column=1)
        entry = tk.Entry(frame, state='disabled', width=50)
        entry.grid(row=0, column=0, stick='we')
        return frame
            
    def _onclose(self):
        """Handle how the ListWindow is closed."""
        
        self._stopPolling()
        self.destroy()
        
    def _stopPolling(self):
        """Stop updating/setting the connected entry i/o widget with
        the value created within the self.pollSet() method."""
        if self.stopcode_set:
            self.after_cancel(self.stopcode_set)
    
    def _assign_rmvbtn(self, field):
        """Assign a button to the provided field that removes the field
        when clicked."""
        
        n = len(self.fields) - 1
        rmvbtn = tk.Button(self.widget_cont, text='-', width=1)
        rmvbtn.config(command=lambda:(
            field.grid_remove(),
            rmvbtn.grid_remove(),
            self.fields.remove(field)
        ))
        rmvbtn.grid(row=n, column=1)
    
    def addEntry(self, s=''):
        """Add an EntryField to the ListWindow"""
        
        n = len(self.fields)
        entfield = EntryField(self.widget_cont, value_name='gnrc', width=50)
        entfield.set(s)
        entfield.grid(row=n, column=0, stick='ew')
        self.fields.append(entfield)
        self._assign_rmvbtn(entfield)
        self.appender.grid(row=n+1)
        
    def addText(self, s=''):
        """Add a TextField to the ListWindow"""
        
        n = len(self.fields)
        txtfield = TextField(self.widget_cont, value_name='gnrc', width=50)
        txtfield.grid(row=n, column=0, stick='ew')
        txtfield.set(s)
        self.fields.append(txtfield)
        self._assign_rmvbtn(txtfield)
        self.appender.grid(row=n+1)
    
    def addSelection(self, s=''):
        """Add a SelectionField to the ListWindow"""
        
        n = len(self.fields)
        selfield = SelectionField(
            self.widget_cont, datpaths=self.datpaths,
            valid_selections=self.valid_selections)
        selfield.set(s)
        selfield.grid(row=n, column=0, stick='ew')
        self.fields.append(selfield)
        self._assign_rmvbtn(selfield)
        self.appender.grid(row=n+1)
        
    def addCompound(self, s=''):
        """Add a CompoundField to the ListWindow"""
        if s == '':
            s = '|+|'
        n = len(self.fields)
        compfield = CompoundField(
            self.widget_cont, datpaths=self.datpaths,
            valid_selections=self.valid_selections, val=s)

        compfield.grid(row=n, column=0, stick='ew')
        self.fields.append(compfield)
        self._assign_rmvbtn(compfield)
        self.appender.grid(row=n+1)
        
    def addConvobit(self, s=''):
        """Add a specifically formatted CompoundField for dealing with
        a specially formatted string used for conversations."""
        if s == '':
            s = '|c|'
        n = len(self.fields)
        selField = CompoundField(
            self.widget_cont,
            sepchar='|c|', 
            val=s, 
            datpaths=[data_path + '/ACTORS.DAT'],
            field_a='selection',
            field_b='text')
            
        selField.grid(row=n, column=0)
        self.fields.append(selField)
        self._assign_rmvbtn(selField)
        self.appender.grid(row=n+1)
        
    def connect(self, textual):
        """Connect a tk.Entry or tk.Text to input/recieve data to/from"""
        
        self.textual = textual
        
    def getValue(self):
        """Get current value inside connected entry"""
        
        return self.textual.get()
      
    def pollSet(self):
        """Continue setting the connected entry value to what is returned from
        self.set()"""
        
        self.set()
        self.stopcode_set = self.after(250, self.pollSet)
      
    def set(self):
        """Set connected entry value to a properly formatted
        list value manifested from values in ListWindow"""
        
        strval = '['
        for field in self.fields:
            val = field.getValue()
            if not val == '':
                strval += str(val) + ','
        strval += ']'
        
        if isinstance(self.textual, tk.Entry):
            start='0'
        elif isinstance(self.textual, tk.Text):
            start='0.0'
            
        self.textual.config(state='normal')
        self.textual.delete(start, 'end')
        self.textual.insert(start, strval)
        self.textual.config(state='disabled')
    
    def append(self, s, field=False):
        """A method that views data within the connected tk.Entry and
        tries to append the appropriate field needed for the value."""
        
        # stop polling setter
        self._stopPolling()
        s = str(s)
        parser = DatParser()
        parser.read(*self.datpaths)
        gob_names = [gob.getAttr('name') for gob in parser.getGobs()]
        
        if s in gob_names:
            self.addSelection(s)
        elif s.find('|+|') != -1:
            self.addCompound(s)
        elif s.find('|c|') != -1:
            self.addConvobit(s)
        elif s.find('\n') != -1:
            self.addText(s)
        else:
            self.addEntry(s)
            
        # start polling again
        self.pollSet()
        
        
class ButtonMenu(tk.Frame):
    """Much like a tk.OptionMenu, a ButtonMenu is just a button that when
    pressed, provides a menu of options."""
    
    def __init__(self, master=None, cnf={}, **kw):
        text = kw.pop('text', '')
        width = kw.pop('width', 1)
        tk.Frame.__init__(self, master, cnf, **kw)
        self.btn = tk.Button(self, text=text, width=width)
        self.btn.grid(row=0, column=0)
        self.menu = tk.Menu(self, tearoff=0)
        self.btn.config(command=self.openSel)
        
    def openSel(self):
        x = self.btn.winfo_rootx() + self.btn.winfo_x() + 34
        y = self.btn.winfo_rooty() + self.btn.winfo_y() + 1
        self.menu.post(x,y)
        
    def add_command(self, **kw):
        self.menu.add_command(**kw)
        
    def config(self, **kw):
        text = kw.pop('text', '')
        self.btn.config(text=text)
        self.config(kw)
        
        
class Editor(object):
    """An Editor for editing and creating GOBs and saving them to .DAT files."""
    
    def __init__(self, root):
        self.root = root
        self.fields = []
        self.fields_current = []
        self.dat_path = ''
        
        # obox/outputbox
        self.obox = OutputBox(root, width=45, height=35)
        self.obox.grid(row=2,column=0, columnspan=4, rowspan=30, stick='ns')
        
        self.obox.addOutput('Initializing...')
        
        # #
        # Create file save & open field
        # #
        
        self.file_frame = tk.Frame(root, 
            highlightbackground='black', highlightthickness=1)
        self.file_frame.grid(row=0, column=0, columnspan=10, stick='we')
        self.file_frame.grid_columnconfigure(2, weight=1)
        self.file_entry = tk.Entry(self.file_frame)
        self.file_entry.grid(row=0, column=2, stick='ewns')
        self.btn_open = tk.Button(self.file_frame, text='o',
            command=self.open, width=2)
        self.btn_open.grid(row=0, column=0, stick='w')
        self.btn_save = tk.Button(self.file_frame, text='s',
            command=self.save, width=2)
        self.btn_save.grid(row=0, column=1, stick='w')
        self.btn_save_as = tk.Button(self.file_frame, text='n',
        command=self.save_as, width=2)
        self.btn_save_as.grid(row=0, column=2, stick='w')
        
        # Bind ctrl+s to self.save()
        root.bind('<Control-s>', lambda _: self.save())
        root.bind('<Control-S>', lambda _: self.save())
        
        # #
        # Create Loaded GOBS dropdown
        # #
        
        self.loaded_frame = tk.Frame(root)
        self.loaded_frame.grid_columnconfigure(0, weight=1)
        self.loaded_frame.grid(row=1, column=0, columnspan=20, stick='ew')
        self.om_gobs_VAR = tk.StringVar(root)
        self.om_gobs_VAR.set('')
        self.om_gobs = tk.OptionMenu(self.loaded_frame, self.om_gobs_VAR,
            *['Empty'])
        self.om_gobs.grid(row=0, column=0, stick='ew')
        self.btn_del = tk.Button(self.loaded_frame, text='DEL',
            command=self.delete)
        self.btn_del.grid(row=0, column=1)
        
        # #
        # Category Selection Menus
        # #
        
        OPTIONS_type = [
            'item',
            'room',
            'actor',
            'conversation',
            'effect',
            'bodypart',
            'map'
        ]
        
        self.obox.addOutput('Added Types: %s' % '\n' + '\n'.join(OPTIONS_type))
        
        self.OPTIONS_subtype = {
            'item': ['consumable', 'equipment'],
            'room': ['room'],
            'actor': ['friendly', 'enemy', 'party'],
            'conversation': ['general', 'room', 'help'],
            'effect': ['effect'],
            'bodypart': ['bodypart'],
            'map': ['map']
        }
        
        self.obox.addOutput('Added subtypes: %s' % (
            '\n' + '\n'.join(self.OPTIONS_subtype)))
        
        # Type selector
        self.lbl_type = tk.Label(root, text='Type')
        self.lbl_type.grid(row=2, column=4)
        
        self.om_type_VAR = tk.StringVar(root)
        self.om_type_VAR.set(OPTIONS_type[0])
        self.om_type = tk.OptionMenu(
            root, 
            self.om_type_VAR,
            *OPTIONS_type,
            command = lambda _: self._typeOptions('type')
        )
        self.om_type.config(width=12)
        self.om_type.grid(row=2, column=5)

        # Subtype selector
        self.lbl_subtype = tk.Label(root, text='Subtype')
        self.lbl_subtype.grid(row=2, column=6)
        
        self.om_subtype_VAR = tk.StringVar(root)
        self.om_subtype_VAR.set(self.OPTIONS_subtype[OPTIONS_type[0]][0])
        self.om_subtype = tk.OptionMenu(
            root,
            self.om_subtype_VAR,
            *self.OPTIONS_subtype[OPTIONS_type[0]],
            command = lambda _: self._typeOptions('subtype')
        )
        self.om_subtype.config(width=12)
        self.om_subtype.grid(row=2, column=7)
        
        # #
        # Field Container
        # #
        
        self.field_container = tk.Frame(root,
        highlightbackground='grey',
        highlightthickness=1
        )
        self.field_container.grid(
            row=3, column=4,
            columnspan=5, rowspan=60, stick='ewns')
        self.field_container.grid_columnconfigure(0, weight=15)
        
        self._update_fields()
        self.obox.addOutput('Added fields: %s' % (
            '\n' + '\n'.join([field.getName() for field in self.fields])
        ))
        
        self.obox.addOutput('Finished!')
        
        
    def _update_fields(self):
        for field in self.fields:
            field.grid_remove()
        del(self.fields)
        self.fields = []
            
        # #
        # Create universal type fields
        # #
        
        self.fields.append(EntryField(self.field_container, value_name='name'))
        self.fields.append(TextField(self.field_container, value_name='desc'))
        
        # # 
        # Create contextual type fields
        # #
        
        # ITEMS
        self.fields.append(EntryField(
            self.field_container, 
            value_name='weight',
            g_type='item'))
        
        # ITEMS - equipment
        self.fields.append(EntryField(
            self.field_container, 
            value_name='defense',
            g_type='item', g_subtype='equipment'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='attack',
            g_type='item', g_subtype='equipment'
            ))
            
        self.fields.append(ListField(
            self.field_container,
            value_name='bodyparts',
            g_type='item', g_subtype='equipment',
            valid_fields=['selection'],
            datpaths=[data_path + '\BODYPARTS.DAT'],
            ))
        
        # ITEMS - consumable
        self.fields.append(EntryField(
            self.field_container, 
            value_name='uses',
            g_type='item', g_subtype='consumable'
            ))
            
        self.fields.append(SelectionField(
            self.field_container,
            datpaths=[data_path + '\EFFECTS.DAT'],
            value_name='effect',
            g_type='item', g_subtype='consumable'
            ))
        
        # ITEMS - key
            # Nothing special (yet)
            
        # ACTORS
        self.fields.append(EntryField(
            self.field_container, 
            value_name='health',
            g_type='actor'
            ))
        
        self.fields.append(ListField(
            self.field_container, 
            value_name='equipped',
            g_type='actor',
            datpaths=[data_path + '/ITEMS.DAT'],
            valid_fields=['selection'],
            valid_selections=['equipment']
            ))
            
        self.fields.append(ListField(
            self.field_container,
            value_name='bodyparts',
            g_type='actor',
            datpaths=[data_path + '/BODYPARTS.DAT'],
            valid_fields=['selection'],
            valid_selections=['bodypart']
        ))
        
        # ACTORS - enemy
            # Nothing special (yet)
         
        # ACTORS - friendly
            # Nothing special (yet)
            
        # ACTORS - party
            # Nothing special (yet)
            
        # ROOMS
        self.fields.append(EntryField(
            self.field_container, 
            value_name='distant',
            g_type='room'
            ))
        
        self.fields.append(ListField(
            self.field_container, 
            value_name='items',
            g_type='room',
            datpaths=[data_path + '/ITEMS.DAT'],
            valid_fields=['selection']
            ))
        
        self.fields.append(ListField(
            self.field_container, 
            value_name='actors',
            g_type='room',
            valid_fields=['selection'],
            datpaths=[data_path + '/ACTORS.DAT']
            ))
        
        # CONVERSATIONS
        self.fields.append(ListField(
            self.field_container,
            value_name='actor',
            datpaths=[data_path + '/ACTORS.DAT'],
            valid_fields=['selection'],
            g_type='conversation'
            ))
            
        self.fields.append(ListField(
            self.field_container,
            value_name='convobits',
            g_type='conversation',
            valid_fields=['convo']
            ))
            
        # EFFECTS
        self.fields.append(EntryField(
            self.field_container,
            value_name='duration',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='rate',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='health',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='defense',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='intelligence',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='dexterity',
            g_type='effect'
            ))
                
        self.fields.append(EntryField(
            self.field_container,
            value_name='strength',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='speak',
            g_type='effect'
            ))
            
        self.fields.append(EntryField(
            self.field_container,
            value_name='agility',
            g_type='effect'
            ))
            
        # MAPS
        self.fields.append(MapField(
            self.field_container,
            value_name='rooms',
            g_type='map',
            datpaths=[data_path + '/ROOMS.DAT'],
            ))
            
        self._load_gob()
        self._typeOptions()
               
    def _typeOptions(self, selected=None, subtype=None):
        """Tries to provide the fields associated with
        the currently selected type and subtype. External sources may need
        to provide specific information via arguments to help provide the right
        fields."""
        
        type = self.om_type_VAR.get().lower()
        if selected == 'subtype':
            subtype = self.om_subtype_VAR.get().lower()
        else:
            if subtype == None:
                subtype = self.OPTIONS_subtype[type][0].lower()
           
        self.om_subtype['menu'].delete(0, 'end')
        self.om_subtype_VAR.set(
            subtype
        )
        
        for key in self.OPTIONS_subtype[type]:
            self.om_subtype['menu'].add_command(
                label=key,
                command=tk._setit(self.om_subtype_VAR,
                key,
                lambda _: self._typeOptions('subtype')))
        
        self.fields_current = []
        
        # Display appropriate fields, remove others
        irow = 2
        for field in self.fields:
            if field.g_type == 'universal':
                self.fields_current.append(field)
                field.grid(row=irow, column=0, stick='nwe')
                irow += 1
            elif field.g_type == type:
                if field.g_subtype == 'general':
                    self.fields_current.append(field)
                    field.grid(row=irow, column=0, stick='nwe')
                    irow += 1
                elif field.g_subtype == subtype:
                    self.fields_current.append(field)
                    field.grid(row=irow, column=0, stick='nwe')
                    irow += 1
                else:
                    field.grid_remove()
            else:
                field.grid_remove()

    def _load_gob(self, *args):
        """Looks at the string recived from currently selected gob in
        self.om_gobs. Read the .DAT found via self.dat_path and find a gob
        with the same name. Load the gob into the currently visiable fields."""
        
        parser = DatParser()
        parser.read(self.dat_path)
        name = self.om_gobs_VAR.get()
        gobs = parser.getGobs()
        found = False
        subtype = None

        if self.om_gobs_VAR.get() == '':
            for field in self.fields:
                field.set('')
            return None
        
        self.obox.addOutput('Loading GOB: %s' % name)
        
        for gob in gobs:
            if gob.getAttr('name') == name:
                
                found = gob
        
        if not found:
            return False
            
        if hasattr(found, 'subtype'):
            subtype = found.getAttr('subtype')
                
        self.om_type_VAR.set(found.getAttr('type'))
        if 'subtype' in found.getAttributes():
            self.om_subtype_VAR.set(found.getAttr('subtype'))
            
        for field in self.fields:
            field.set('')
               
            if field.getName() in found.getAttributes():
                field.set(found.getAttr(field.getName()))
        self._typeOptions(None, subtype)
        
        self.obox.addOutput('GOB load success!')
        
    def open(self):
        """Open a .DAT file and then load the first GOB in 
        the self.om_gobs menu."""
        
        path = askopenfilename(initialdir=data_path, filetypes=[('DAT file','*.DAT')])
        if path == '':
            return None
        self.obox.addOutput("Loading file...")
        
        self.file_entry.delete(0, 'end')
        self.file_entry.insert(0, path)
        
        parser = DatParser()
        failed = parser.read(path)
        # parser.read() method returns a list of file paths that failed to open
        for failure in failed:
            self.obox.addOutput("Failed to open: '%s'" % failure)
        
        self.dat_path = path
        
        gobs = parser.getGobs()
        
        if len(gobs) != 0:
            self.om_gobs['menu'].delete(0, 'end')
            self.om_gobs_VAR.set(
                gobs[0].getAttr('name')
            )
            
        # Empty GOB selection option
        self.om_gobs['menu'].add_command(
                label='',
                command=tk._setit(self.om_gobs_VAR,
                '',
                self._load_gob))
        self.om_gobs_VAR.set('')
        
        # Add all located GOBs to selection
        for gob in gobs:
            name = gob.getAttr('name')
            self.om_gobs['menu'].add_command(
                label=name,
                command=tk._setit(self.om_gobs_VAR,
                name,
                self._load_gob))
            self.obox.addOutput('GOB Added: ' + gob.getAttr('name'))
        
        self.obox.addOutput("File loaded succesfully!")
        self._load_gob()
    
    def save(self):
        """Save the current gob to the current .DAT. If no current .DAT,
        call self.save_as()"""
        
        try:
            with open(self.file_entry.get()) as f:
                pass
            if self.dat_path != '':
                self.obox.addOutput('Saving...')
                parser = DatParser()
                parser.read(self.dat_path)
            else:
                self.save_as()
                return None

        except FileNotFoundError:
            self.save_as()
            return None
        
        # Get header
        for field in self.fields_current:
            if field.value_name == 'name':
                header = field.getValue()
                if header == '':
                    self.obox.addOutput('Save Failed: Please provide a name!')
                    return False
                    
                break
        
        if header in parser.getRaws():
            self.obox.addOutput('Updating GOB: %s' % header)
            for field in self.fields_current:
                if field.getName() == 'name':
                    continue
                name = field.getName()
                value = field.getValue()
                parser.updateValue(header, name, value)
                self.obox.addOutput('Updated %s' % name)
        else:
            self.obox.addOutput('New GOB: %s' % header)
            parser.addHeader(header)
            for field in self.fields_current:
                name = field.getName()
                value = field.getValue()
                parser.addName(header, name, value)
                self.obox.addOutput('Updated %s' % name)
                
            
            self.om_gobs['menu'].add_command(
                    label=header,
                    command=tk._setit(self.om_gobs_VAR,
                    header,
                    self._load_gob))
                
        if not 'type' in parser.getRaws():
            parser.addName(header, 'type', self.om_type_VAR.get())
        else:
            print(parser.getRaws())
        if not 'subtype' in parser.getRaws():
            parser.addName(header, 'subtype', self.om_subtype_VAR.get())
            
        parser.save()
        
        self.om_gobs_VAR.set(header)
        self.obox.addOutput('Updating fields...')
        
        # Currently I update fields to make sure SelectionFields have relevent
        # info. It's quick and dirty and shouldn't be hard to implement
        # something cleaner. 
        #( _update_fields() causes window to twitch when called. Not pretty. )
        self._update_fields()
        
        self.obox.addOutput('Saved!')
        
    def save_as(self):
        """Create a new .DAT file to be saved to."""
        
        path = asksaveasfilename(initialdir=data_path, filetypes=[('DAT File', '*.DAT')])
        if path == '':
            return None
        if not path.endswith('.DAT'):
            path += '.DAT'
        self.dat_path = path
        with open(path, 'w'):
            pass
        self.obox.addOutput('Created %s' % os.path.basename(path))
        self.file_entry.delete(0, 'end')
        self.file_entry.insert(0, path)
        self.save()

    def delete(self):
        """Delete the currently selected GOB in the self.om_gobs menu."""
        
        selected = self.om_gobs_VAR.get()
        if selected == '':
            return None
            
        yes = messagebox.askyesno('WARNING!','Are you sure you want to delete \'%s?\'' % selected)
        if yes:
            pass
        else:
            return None
       
        self.obox.addOutput('Deleting %s...' % selected)
        
        parser = DatParser()
        parser.read(self.dat_path)
            
        parser.delete(selected)
        gobs = parser.getGobs()
        
        self.om_gobs['menu'].delete(1, 'end')
        for gob in parser.getGobs():
            name = gob.getAttr('name')
            self.om_gobs['menu'].add_command(
                label=name,
                command=tk._setit(self.om_gobs_VAR,
                name,
                self._load_gob))
        self.om_gobs_VAR.set('')
        
        self.obox.addOutput('Deletion Successful!')
        self._load_gob()
        
        
def main():
    root = tk.Tk()
    root.resizable(1,0)
    root.grid_columnconfigure(8, weight=1)
    root.title('Editor')
    editor = Editor(root)
    tk.mainloop()
    
if __name__ == '__main__':
    main()