from PySide6.QtGui import QBrush, QPen, Qt

from graph import QGraphicsRoundedRectangleItem
from programcon import *


def convertHEX2RGBA(src:str):
    r = int(src[1:3], 16)
    g = int(src[3:5], 16)
    b = int(src[5:7], 16)
    return (r, g, b)

def convertMemory(src:int) -> str:
    lst = (" B", " KB", " MB", " GB", " TB", " PB", " EB", " ZB", " YB")
    chunk = 1024
    for i in lst:
        if src < chunk:
            return str(int(src*100)/100) + i
        src /= chunk
    return str(int(src*100)/100) + "YB"

def makeQGraphicsRoundedRectangle(x:float, y:float, width:float, height:float, pen:QPen=Qt.NoPen, brush:QBrush=Qt.NoBrush) -> QGraphicsRoundedRectangleItem:
    
    item = QGraphicsRoundedRectangleItem()
    item.setPenDefault(pen)
    item.setBrush(brush)
    item.setRadius(RADIUS)
    item.setPos(x, y)
    item.setSize(width, height)
    return item
