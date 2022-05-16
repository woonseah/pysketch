# pysketch
Processing-like sketch programs but for Python projects **(on Windows)***

## Dependencies
PySketch uses the following packages:
 * ```tkinter``` as the sketch GUI Window
 * ```Pillow/PIL``` for the canvas, drawing tools, font and Tk interface
 * ```pynput``` for capturing inputs from mouse and keyboard
 * ```numpy``` for processing the input image to draw on the screen
 * ```ctypes``` for getting the display screen size* **(platform-dependent, Windows only)**
 * ```pywin32``` for checking if sketch window is being focused* **(platform-dependent, Windows only)**

Since this is a personal project, I wrote this without platform-cross-compatibility in mind or adding crazy amounts of error-handling. All I can say is that it works on my machine running Windows 10. 😅 If you need compatibility for operating systems other than Windows, you'll need to write your own implementation without using the `pywin32` or the `ctypes` module.
## Usage
Place the `pysketch.py` module somewhere where you can access from python and import from. (You'll also need a .ttf font file as default font or text drawing will not work correctly, change the code at `Line 279: _font_file: str = '<your-font-file>.ttf'` )

Once done, simply create a new python `.py` script following the template below and run your sketch. For examples, check out the [`examples`](examples) folder.
```python
from pysketch import *

def setup():
    # setup code goes here
    pass

def draw():
    # draw code goes here
    pass

if __name__ == '__main__':
    PySketch(globals())
```
### User-defined Functions
 - `setup()` : code here runs once when the program starts
 - `draw()` : code here runs continuously until the program ends
 - `keyPressed()`/`keyPressed(key: str)` : called whenever a key is pressed
 - `keyReleased()`/`keyReleased(key: str)` : called whenever a key is released
 - `mouseMoved()`/`mouseMoved(x: int, y: int)` : called when mouse is moved
 - `mousePressed()`/`mousePressed(button: int)` : called when mouse is pressed
 - `mouseReleased()`/`mouseReleased(button: int)` : called when mouse is released
 - `mouseWheel()`/`mouseWheel(amount: int)` : called when mouse is scrolled
### Global Variables (read-only)
`width`, `height`, `displayWidth`, `displayHeight`, `mouseX`, `mouseY`, `key`, `mouseButton`, `focused`
### GUI and System Functions
 - `size(width: int, height: int)` : sets the dimensions of the sketch window.
 - `set_title(text: str)` : sets the title of the sketch window.
 - `set_resizable(resize: bool)` : sets whether resizing is enabled on the sketch window.
 - `set_window_location(x: int, y: int)` : sets the window location of the sketch window.
 - `millis()` : gets the time in milliseconds since the start of the sketch.
 - `delay(duration_ms: int)` : delay for the given duration in milliseconds.
### Styling Functions
 - `fill(...)`**^** : sets the fill color when drawing shapes on the canvas.
 - `stroke(...)`**^** : sets the stroke color when drawing strokes on the canvas.
 - `noFill()` : disable fill with color where possible when drawing on the canvas.
 - `noStroke()` : disable drawing stroke where possible when drawing on the canvas.
### Canvas Drawing Functions
 - `background(...)`**^** : clears the sketch canvas with the given input color.
 - `rect(x, y, w, h)` : draws a rectangle with given dimensions on the sketch canvas.
 - `line(x1, y1, x2, y2)` : draws a line between two points on the sketch canvas.
 - `image(img, x, y)`/`image(img, x, y, w, h)` : draws the input Image or numpy array at the given position and dimensions.
 - `textSize(size)` : sets the font text size used when drawing text.
 - `text(string, x, y)` : draws the input text at the given position in the sketch canvas.


**^accepted arguments :**  `<function>(gray)`, `<function>(gray, alpha)`, `<function>(r, g, b)`, or `<function>(r, g, b, alpha)`

## Why?
I have been using Processing 3 (Java) to write my programming projects for quite some time but started facing problems with importing external `.jar` libraries which my project requires into the Processing environment. I could switch to using Eclipse IDE and write the Java program from scratch but the whole point of using Processing was to avoid this. ~~(PTSD of Eclipse slow compiles and missing imports)~~

At this point, I switched to using python for my programming projects as I found it really easy to install packages using `pip`. However, after switching to python, I missed having the simplicity of only having setup() and draw() functions, and everything else running by itself like magic. GUI packages like Tkinter are powerful but a little too complex to setup, eating up precious development time for me. With this idea in mind, I wrote this `pysketch` project to help with development time when working with python.

Side Note: Also why not use `pyprocessing`? Uhh... good point. Haha. (I have no idea how to use that 😑)
## Contributing
Pull requests are welcome!


**TODO:** `ellipse`, `textAlign`, `textFont`, `strokeWeight`, `noLoop`, `frameRate`, `translate`, `scale`, `rotate`, `push`, `pop`

## License
[MIT License](https://choosealicense.com/licenses/mit/)
