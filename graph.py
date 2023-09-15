import random

# import taichi
from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem


def randomColor() -> tuple[int]:

    if random.randint(0, 5) & 1:
        r = random.randint(25, 75)
        g = random.randint(0, 50)
        b = random.randint(200, 255)
    elif random.randint(0, 2) & 1:
        r = random.randint(150, 255)
        g = random.randint(150, 255)
        b = random.randint(150, 255)
    else:
        r = random.randint(200, 255)
        g = random.randint(0, 50)
        b = random.randint(200, 255)
    return r, g, b

class QGraphicsRoundedRectangleItem(QGraphicsItem):

    def __init__(self, parent=None):

        super().__init__(parent)

        # size
        self._node_width = 240
        self._node_height = 160
        self._node_radiusx = 0
        self._node_radiusy = 0

        # pen
        self._pen_default = Qt.NoPen#QPen(QColor("#151515"))
        self._pen_selected = QPen(QColor("#aaffee00"))

        # brush
        self._brush_background = QBrush(QColor("#aa151515"))
    
    def boundingRect(self) -> QRectF:

        return QRectF(0, 0, self._node_width, self._node_height)
    
    def paint(self, painter: QPainter, option, widget):
        
        node_outline = QPainterPath()
        node_outline.addRoundedRect(0, 0, self._node_width, self._node_height, self._node_radiusx, self._node_radiusy)

        painter.setPen(self._pen_default)
        painter.setBrush(self._brush_background)
        painter.drawPath(node_outline.simplified())

    def setSize(self, width:float, height:float):

        self._node_width = width
        self._node_height = height

    def setWidth(self, width:float):

        self._node_width = width

    def setHeight(self, height:float):

        self._node_height = height

    def setRadius(self, radius:float):

        self._node_radiusx = self._node_radiusy = radius

    def setRadiusX(self, radiusx:float):

        self._node_radiusx = radiusx

    def setRadiusY(self, radiusy:float):

        self._node_radiusy = radiusy

    def setPenDefault(self, pen:QPen):

        self._pen_default = pen

    def setPenSelected(self, pen:QPen):

        self._pen_selected = pen

    def setBrush(self, brush:QBrush):

        self._brush_background = brush

class QGraphicsRoundedRectangleImageItem(QGraphicsPixmapItem):

    def __init__(self, parent=None):

        super().__init__(parent)

        # size
        self._node_width = 240
        self._node_height = 160
        self._node_radiusx = 0
        self._node_radiusy = 0

        # image
        self._image = QPixmap()
    
    def pixmap(self) -> QPixmap:

        if self._image is None:
            return QPixmap()
        width = self._image.width()
        width = self._node_width
        height = self._image.height()
        height = self._node_height
        new = self._image.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        res = QPixmap(new.width(), new.height())
        res.fill(Qt.transparent)
        painter = QPainter(res)
        painter.setRenderHints(QPainter.Antialiasing, True)
        painter.setRenderHints(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        rect = QRectF(0, 0, new.width(), new.height())
        path.addRoundedRect(rect, self._node_radiusx, self._node_radiusy)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, new.width(), new.height(), new)
        return res
    
    def boundingRect(self) -> QRectF:

        return QRectF(0, 0, self._node_width, self._node_height)
    
    def paint(self, painter: QPainter, option, widget):

        pixmap = self.pixmap()
        painter.drawPixmap(self._node_width//2-pixmap.width()//2, self._node_height//2-pixmap.height()//2, pixmap.width(), pixmap.height(), pixmap)

    def setSize(self, width:float, height:float):

        self._node_width = width
        self._node_height = height

    def setWidth(self, width:float):

        self._node_width = width

    def setHeight(self, height:float):

        self._node_height = height

    def setRadius(self, radius:float):

        self._node_radiusx = self._node_radiusy = radius

    def setRadiusX(self, radiusx:float):

        self._node_radiusx = radiusx

    def setRadiusY(self, radiusy:float):

        self._node_radiusy = radiusy

class QGraphicsRoundedRectangleExpandingImageItem(QGraphicsPixmapItem):

    def __init__(self, parent=None):

        super().__init__(parent)

        # size
        self._node_width = 240
        self._node_height = 160
        self._node_radiusx = 0
        self._node_radiusy = 0

        # image
        self._image = QPixmap()
    
    def pixmap(self) -> QPixmap:

        if self._image is None:
            return QPixmap()
        width = self._image.width()
        width = self._node_width
        height = self._image.height()
        height = self._node_height
        new = self._image.scaled(width, height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        new = new.copy(new.width()/2-width/2, new.height()/2-height/2, width, height)
        res = QPixmap(new.width(), new.height())
        res.fill(Qt.transparent)
        painter = QPainter(res)
        painter.setRenderHints(QPainter.Antialiasing, True)
        painter.setRenderHints(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        rect = QRectF(0, 0, new.width(), new.height())
        path.addRoundedRect(rect, self._node_radiusx, self._node_radiusy)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, new.width(), new.height(), new)
        return res
    
    def boundingRect(self) -> QRectF:

        return QRectF(0, 0, self._node_width, self._node_height)
    
    def paint(self, painter: QPainter, option, widget):

        pixmap = self.pixmap()
        painter.drawPixmap(self._node_width//2-pixmap.width()//2, self._node_height//2-pixmap.height()//2, pixmap.width(), pixmap.height(), pixmap)

    def setSize(self, width:float, height:float):

        self._node_width = width
        self._node_height = height

    def setWidth(self, width:float):

        self._node_width = width

    def setHeight(self, height:float):

        self._node_height = height

    def setRadius(self, radius:float):

        self._node_radiusx = self._node_radiusy = radius

    def setRadiusX(self, radiusx:float):

        self._node_radiusx = radiusx

    def setRadiusY(self, radiusy:float):

        self._node_radiusy = radiusy