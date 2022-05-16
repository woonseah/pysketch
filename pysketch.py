import os
import time
import ctypes
import win32gui
import traceback
import numpy as np
from tkinter import *
from tkinter import ttk
from pynput import mouse, keyboard
from PIL import Image, ImageTk, ImageDraw, ImageFont

class PySketch:
    def __init__(self, globals: dict) -> None:
        global _sketch
        self._globals = globals
        _sketch = self
        self.start()
    
    _window: Tk = None
    _window_x: int = None
    _window_y: int = None
    _window_title: str = ''
    _window_width: int = 0
    _window_height: int = 0
    _window_resizable: bool = False
    _window_exit_flag: bool = False
    def _init_window(self):
        self._window = Tk()
        self._window.title(self._window_title)
        self._window.minsize(168, 168)
        self._window.geometry('{w}x{h}'.format(w=self._width, h=self._height))
        self._window.resizable(self._window_resizable, self._window_resizable)
        # Sketch's canvas image will be drawn in this label
        self._window_frame = Label(self._window)
        self._window_frame.pack(fill='both', expand=1)
        # Makes _window_exit_flag set when window is closed by user
        def on_quit():
            self._window_exit_flag = True
            self._window.destroy()
        self._window.protocol('WM_DELETE_WINDOW', on_quit)

    _width:int = 0
    _height:int = 0
    _displayWidth:int = 0
    _displayHeight:int = 0
    _key: str = ''
    _mouseX:int = 0
    _mouseY:int = 0
    _mouseButton:int = 0
    _focused: bool = False
    def _update_global_vars(self): # faster than using self._globals.update({...})
        global width, height, displayWidth, displayHeight, key, mouseX, mouseY, mouseButton, focused
        width, height, displayWidth, displayHeight, mouseX, mouseY, mouseButton, focused = self._width, self._height, self._displayWidth, self._displayHeight, self._mouseX, self._mouseY, self._mouseButton, self._focused
    
    _mouse_listener: mouse.Listener = None
    _keyboard_listener: keyboard.Listener = None
    def __on_key_press(self, key):
        if (not self._focused): return
        self._key = key
        consumed = False
        try: # accepted: keyPressed() or keyPressed(key)
            self._update_global_vars()
            try: consumed = self._globals['keyPressed'](key)
            except: consumed = self._globals['keyPressed']()
        except: pass
        if (key == keyboard.Key.esc and not consumed):
            self._window_exit_flag = True
            self._window.destroy()
    def __on_key_release(self, key):
        if (not self._focused): return
        self._key = key
        try: # accepted: keyReleased() or keyReleased(key)
            try: self._globals['keyReleased'](key)
            except: self._globals['keyReleased']()
        except: pass
    def __on_mouse_move(self, x, y):
        over_window = self._update_mouse_position(x, y)
        if (not self._focused or not over_window): return
        try: # accepted: mouseMoved() or mouseMoved(x, y)
            try: self._globals['mouseMoved'](x, y)
            except: self._globals['mouseMoved']()
        except: pass
    def __on_mouse_click(self, x, y, button, pressed):
        over_window = self._update_mouse_position(x, y)
        if (not self._focused or not over_window): return
        self._mouseButton = button
        if (pressed):
            try: # accepted: mousePressed() or mousePressed(button)
                try: self._globals['mousePressed'](button)
                except: self._globals['mousePressed']()
            except: pass
        else:
            try: # accepted: mouseReleased() or mouseReleased(button)
                try: self._globals['mouseReleased'](button)
                except: self._globals['mouseReleased']()
            except: pass
    def __on_mouse_scroll(self, x, y, dx, dy):
        if (not self._focused): return
        self._update_mouse_position(x, y)
        try: # accepted: mouseWheel() or mouseWheel(amt)
            try: self._globals['mouseWheel']()
            except: self._globals['mouseWheel'](dy) # (only dy changes?)
        except: pass
    def _update_mouse_position(self, x: int, y: int):
        x -= self._window_x + 7
        y -= self._window_y + 31
        if (x < 0 or y < 0 or x > self._width or y > self._height): return False
        self._mouseX, self._mouseY = x, y
        return True
    def _hook_inputs(self):
        self._keyboard_listener = keyboard.Listener(
            on_press=self.__on_key_press, on_release=self.__on_key_release)
        self._mouse_listener = mouse.Listener(
            on_move=self.__on_mouse_move, on_click=self.__on_mouse_click,
            on_scroll=self.__on_mouse_scroll)
        
        self._keyboard_listener.start()
        self._mouse_listener.start()
        # do we help to initialize mouse position or wait for mouse to move?
        # in Processing, mouseX and mouseY only updates when the mouse moves.
        x,y = mouse.Controller().position
        self.__on_mouse_move(x,y)

    _canvas: Image = None
    _sketch_start_time: float = None
    _update_window_flag: bool = False
    def start(self):
        self._window_title = 'PySketch - {name}'.format(name= os.path.basename(self._globals['__file__']))
        self._displayWidth, self._displayHeight = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self._font = ImageFont.truetype(self._font_file, self._font_size)
        
        self._sketch_start_time = time.time() # this goes before _run_setup()
        try: # Run user-defined setup() function
            if ('setup' not in self._globals or not callable(self._globals['setup'])):
                raise Exception('setup() function is missing or not callable.')
            self._update_global_vars()
            self._globals['setup']()
        except Exception as ex:
            print('\nSketch failed to run due to exception in setup():\n\n{}'.format(''.join(traceback.format_exception(ex))))
            return
        self._init_window()
        self._window.wait_visibility()
        
        # what happens during a resize? will _canvas update mid-draw or only on next draw?
        if (self._window_x is None and self._window_y is None):
            _, _, _x, _y = [int(e) for e in self._window.geometry().replace('x', '+').split('+')]
            self._window_x = _x 
            self._window_y = _y
        self._hook_inputs()
        
        while not self._window_exit_flag:
            _w, _h, _x, _y = [int(e) for e in self._window.geometry().replace('x', '+').split('+')]
            
            if self._update_window_flag:
                self._update_window_flag = False
                # Update window title
                if (self._window.title() != self._window_title): self._window.title(self._window_title)
                # Update window resizable
                if (self._window.resizable() != (self._window_resizable, self._window_resizable)):
                    self._window.resizable(self._window_resizable, self._window_resizable)
                self._window.geometry('{w}x{h}+{x}+{y}'.format(
                    # Windows 10 have an invisible border of 7 pixels! Nice.
                    w= self._width, h= self._height, x= (self._window_x - 7), y= self._window_y
                ))
            # if window is not resizable, _width and _height would be fixed value
            # do we need to set it back?
            self._width, self._height = _w, _h
            self._window_x, self._window_y = _x, _y
            self._focused = win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self._window_title
            # check if we need to update canvas size
            if (self._canvas is None or self._canvas.size != (self._width, self._height)):
                self._canvas = Image.new('RGBA', (self._width, self._height), (192,192,192,255))
                self._imgdraw = ImageDraw.Draw(self._canvas)
            
            try: # Run user-defined draw function
                self._update_global_vars()
                self._globals['draw']()
            except Exception as ex:
                print('\nAn exception occurred in draw():\n\n{}'.format(''.join(traceback.format_exception(ex))))
                self._window_exit_flag = True
                self._window.destroy()
                continue
            
            self._output = ImageTk.PhotoImage(self._canvas)
            self._window_frame.configure(image=self._output)
            self._window.update_idletasks()
            self._window.update()
        
        self._mouse_listener.stop()
        self._keyboard_listener.stop()
        
    def size(self, w: int, h: int):
        self._width, self._height = int(w), int(h)
        self._update_window_flag = True
    def set_title(self, text: str):
        self._window_title = str(text)
        self._update_window_flag = True
    def set_resizable(self, resizable: bool):
        self._window_resizable = bool(resizable)
        self._update_window_flag = True
    def set_window_location(self, x: int, y: int):
        self._window_x, self._window_y = int(x), int(y)
        self._update_window_flag = True
    
    def millis(self):
        return round((time.time() - self._sketch_start_time) * 1000)
    
    _noFill:bool = False
    _noStroke:bool = False
    _fillColor: tuple = (255, 255, 255, 255)
    _strokeColor: tuple = (0, 0, 0, 255)
    _strokeWeight: int = 1

    def fill(self, args: list):
        self._noFill, self._fillColor = False, self._args_to_rgba(args)
    def stroke(self, args: list):
        self._noStroke, self._strokeColor = False, self._args_to_rgba(args)
    
    def noFill(self): self._noFill = True
    def noStroke(self): self._noStroke = True

    @staticmethod
    def _args_to_rgba(args:list):
        args = [int(e) for e in args]
        args_len = len(args)
        try:
            return (
                args[0], # gray / r
                args[0 if args_len < 3 else 1], # gray / g
                args[0 if args_len < 3 else 2], # gray / b
                args[-1] if (args_len % 2 == 0) else 255 # alpha
            )
        except: raise TypeError('unable to get rgba from args: {}'.format(args))

    def background(self, args):
        self._imgdraw.rectangle(
            xy= [(0,0),(self._width, self._height)],
            fill= self._args_to_rgba(args),
            outline= None, width= 0)
    
    def rect(self, x: int, y: int, w: int, h: int):
        x,y,w,h = int(x), int(y), int(w), int(h)
        self._imgdraw.rectangle(
            xy= [(x,y), (x+w, y+h)],
            fill= None if self._noFill else self._fillColor,
            outline= None if self._noStroke else self._strokeColor,
            width= 0 if self._noStroke else self._strokeWeight)
    def line(self, x1: int, y1: int, x2: int, y2: int):
        x1,y1,x2,y2 = int(x1), int(y1), int(x2), int(y2)
        self._imgdraw.line(
            xy=[(x1,y1),(x2,y2)],
            fill= self._strokeColor,
            width= self._strokeWeight
        )
    def image(self, args):
        if len(args) not in [3, 5]: raise TypeError('Bad arguments for image function.')
        resize_image: bool = (len(args) == 5)
        inp, x, y = args[:3]

        img = None
        if (type(inp) == np.ndarray):
            if (len(inp.shape) == 2):
                # binary image, so we scale it up and then make it RGB
                img = Image.fromarray(np.stack((inp*255,)*3, axis=-1), 'RGB')
            elif (len(inp.shape) == 3):
                img = Image.fromarray(inp, 'RGBA' if (inp.shape[2] == 4) else 'RGB')
        elif (type(inp) == Image.Image):
            img = inp
        else: raise Exception('not sure how to convert {} to PIL.Image:\ninp={}'.format(type(inp), inp))
        
        w, h = img.size
        if (resize_image):
            w, h = args[3:5]
            img = img.resize((int(w), int(h)))
        
        self._canvas.paste(img, (int(x), int(y)))

    _font: ImageFont = None
    _font_file: str = 'CenturyGothic_v2.3.ttf'
    _font_size: int = 20
    
    def textSize(self, size: int):
        self._font_size = size
        self._font = ImageFont.truetype(self._font_file, self._font_size)

    def text(self, text: str, x: float, y: float):
        text, x, y = str(text), int(x), int(y)
        self._imgdraw.text((x, y), text, self._fillColor, self._font)
    
    

_sketch:PySketch = None

width: int = 0
height: int = 0
displayWidth: int = 0
displayHeight: int = 0
key: str = ''
mouseX: int = 0
mouseY: int = 0
mouseButton: int = 0
focused: bool = False
def size(width: int, height: int):
    """Sets the dimensions of the program sketch window."""
    return _sketch.size(width, height)
def set_title(text: str):
    """Sets the title of the sketch window."""
    return _sketch.set_title(text)
def set_resizable(resizable: bool):
    """Sets whether the program sketch window can be resized."""
    return _sketch.set_resizable(resizable)
def set_window_location(x: int, y: int):
    """Sets the location of the program sketch window."""
    return _sketch.set_window_location(x, y)
def millis() -> int:
    """Gets the time in milliseconds since the start of the sketch."""
    return _sketch.millis()
def fill(*args):
    """Sets the fill color when drawing shapes in the sketch.
    * fill(gray)
    * fill(gray, alpha)
    * fill(r, g, b)
    * fill(r, g, b, alpha)"""
    return _sketch.fill(args)
def stroke(*args):
    """Sets the stroke color when drawing shapes in the sketch.
    * stroke(gray)
    * stroke(gray, alpha)
    * stroke(r, g, b)
    * stroke(r, g, b, alpha)"""
    return _sketch.stroke(args)
def noFill():
    """Sets the renderer to not fill when drawing shapes."""
    return _sketch.noFill()
def noStroke():
    """Sets the renderer to not outline when drawing shapes."""
    return _sketch.noStroke()
def background(*args):
    """Clears the sketch window with the given input color.
    * background(gray)
    * background(gray, alpha)
    * background(r, g, b)
    * background(r, g, b, alpha)"""
    return _sketch.background(args)
def rect(x: float, y: float, width: float, height: float):
    """Draws a rectangle with given dimensions on the program sketch window."""
    return _sketch.rect(x, y, width, height)
def line(x1: float, y1: float, x2: float, y2: float):
    """Draws a line between two points on the sketch window."""
    return _sketch.line(x1, y1, x2, y2)
def image(*args):
    """Draws the input image at the given position and dimensions.
    * image(img, x, y)
    * image(img, x, y, width, height)"""
    return _sketch.image(args)
def textSize(size: int):
    """Sets the font text size used when drawing text."""
    return _sketch.textSize(size)
def text(string: str, x: float, y: float):
    """Draws the input text at the given position in the sketch."""
    return _sketch.text(string, x, y)

def run_test():
    def setup():
        #set_title('PySketch Demo and Test')
        pass
    def draw():
        pass
    globals().update({
        'setup': setup,
        'draw': draw
    })
    PySketch(globals())

if __name__ == '__main__':
    run_test()
