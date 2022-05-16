from pysketch import *

def setup():
    size(600, 400)
    set_title('PySketch Demo and Test')
    set_resizable(True)

def draw():
    #background(255)
    fill(255,0,0)
    rect(mouseX-25, mouseY-25, 50, 50)

def mousePressed():
    print('mouse pressed!')

def keyPressed(key):
    print('{} was pressed!'.format(key))

if __name__ == '__main__':
    PySketch(globals())
