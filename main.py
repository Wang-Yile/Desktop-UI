"""
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple
matplotlib
Pillow
opencv-python
pyaudio
psutil
requests
PySide6
"""

import os
import sys

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QMouseEvent, QPen
from PySide6.QtWidgets import (QApplication, QGraphicsDropShadowEffect,
                               QGraphicsScene, QGraphicsTextItem,
                               QGraphicsView, QLineEdit, QMainWindow)

import program as winProgram
# import window as winEffect
from graph import *
from programapi import convertHEX2RGBA
from programcon import *

"""
附注 关于 ZValue 的说明^
[-inf,0) 系统保留
0 默认
(0,100) 系统保留
  50: 标签栏关闭按钮
[100,200) 标签页
[200,300) 弹出菜单
[300,1000) 消息系统&顶层会话框
  300: 消息框底层颜色
  350: 消息框标题, 选项等
  400: 消息框信息
[1000,inf] 系统保留
"""

# HOMEPAGE_CRYSTAL_BALL_COLOR = "#523d8f"

if __name__ == "__main__":

    # MENU_URL_INDEX = {
    #     ">homepage": winProgram.HomePage,
    #     ">monitor": winProgram.Monitor,
    #     ">calculator": winProgram.Calculator,
    #     ">note": "速记",
    #     ">todo": "待办事项",
    #     ">datetime": "时间&日期",
    #     ">weather": "天气",
    #     ">mediacenter": winProgram.MediaCenter,
    #     ">encryption": "数据加密",
    #     ">decryption": "数据解密",
    #     ">steganography": "数据隐写",
    #     ">settings": "设置",
    #     ">newtab": "新标签页"
    # }
    MENU_URL_INDEX = {}
    for i in winProgram.__all__:
        tmp:winProgram.BaseProgram = eval("winProgram.%s"%i)
        MENU_URL_INDEX[tmp.location.lower()] = tmp

def clearTemp():

    for i in os.listdir(os.getenv("temp")):
        if i[:12] == "cached-sound":
            os.remove(os.getenv("temp")+"\\"+i)

def exitProgram():

    for i in window._menu:
        i.close()
    window.hide()
    try:
        clearTemp()
    except PermissionError as msg:
        print("PermissionError:", msg)
    finally:
        sys.exit(0)

class MainWindow(QGraphicsView):

    def __init__(self):
        
        super().__init__()

        self._onMoveDrag = False
        self._onResizeDrag = False
        self._onLeftButton = False
        self._onLeftDrag = False
        self._onLeftRealDrag = False
        self._onLeftDragIndex = 0
        self._onLeftDragToIndex = 0
        self._onLeftHighLightIndex = 0
        self._old_height = None
        self._old_width = None
        self._old_bottom = None
        self._old_right = None
        self._old_top = None
        self._old_left = None
        self.mouse_press_pos = None
        self.mouse_now_pos = None
        self.mouse_now_realPo = None
        self.mouse_leftdrag_pos = None
        self._configured = True
        self._closed = False
        self._closeCount = 0
        self._group = []
        self._per_left = 150

        self._focusLocation = True
        self._location = ""

        self._pageGroup = []
        self._messageGroup = []
        self._mainGroup = []
        self._leftButtonXBackgroundItem = None # 标签栏的关闭按钮背景

        self._messages = []
        self.addMessage(5, "欢迎", "Desktop UI 是自由软件，你可以在 GitHub 上查找和获取它的免费更新。", "system", [["了解详情", "https://github.com/Wang-Yile/Desktop-UI"], ["不再提示", "system:no_mention"]])

        self._scene = QGraphicsScene()
        self._scene.setBackgroundBrush(Qt.NoBrush)
        self.setBackgroundBrush(Qt.NoBrush)
        self.setScene(self._scene)

        self.setWindowTitle("桌面")
        self.setMinimumSize(400, 200)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint) # Qt.WindowStaysOnTopHint
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: rgb(0, 0, 0); border-radius: %dpx" % RADIUS)
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(10)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)
        # self.setWindowOpacity(0.8)
        self.resize(1280, 720)

        # self._win_effect = winEffect.WindowEffect()
        # self._win_effect.addShadowEffect(self.winId())

        # self._timerId = self.startTimer(CHUNK)
        self._chunk = CHUNK
        self._pageChunk = CHUNK
        self._timer = QTimer()
        self._timer.setInterval(self._chunk)
        self._timer.start()
        self._timer.timeout.connect(self.timer)
        self._pageTimer = QTimer()
        self._pageTimer.setInterval(self._pageChunk)
        self._pageTimer.start()
        self._pageTimer.timeout.connect(self.pageTimer)
        self._messageTimer = QTimer()
        self._messageTimer.setInterval(100)
        self._messageTimer.start()
        self._messageTimer.timeout.connect(self.messageTimer)

        self._menu:list[winProgram.BaseProgram] = [
            winProgram.Calculator(self)
        ]
        self._startY = 60
        self._index = 0
    
    def calculateLeftWidth(self) -> float:

        if self._per_left < 1:
            return self.width()*self._per_left
        return self._per_left
    
    def calculateRightWidth(self) -> float:

        return self.width()-self.calculateLeftWidth()-10
    
    def calculateLeftIndex(self, realY) -> int:

        return int((realY - self._startY) / 35)
    
    def calculateLeftY(self, index) -> int:

        return self._startY + index*35

    def addMessage(self, tick:int=5, title:str="", message:str="", source:str="unknown", option:list[list[str,str]]=[]):

        self._messages.append([tick, title, message, source, option])

    def mousePressEvent(self, event):

        toUpdate = False
        if event.button() == Qt.LeftButton:
            self._onLeftButton = True
            frame_rect = self.frameGeometry()
            self._old_left = frame_rect.left()
            self._old_top = frame_rect.top()
            self._old_right = frame_rect.right()
            self._old_bottom = frame_rect.bottom()
            self._old_width = frame_rect.width()
            self._old_height = frame_rect.height()
            self.mouse_press_pos = event.globalPosition().toPoint()
            realX = self.mouse_press_pos.x() - self._old_left
            realY = self.mouse_press_pos.y() - self._old_top
            self._resizeMode = None
            if abs(self.mouse_press_pos.x() - self._old_left) < SENSITIVITY:
                self._onResizeDrag = True
                if not self._resizeMode:
                    self._resizeMode = Qt.LeftEdge
                else:
                    self._resizeMode |= Qt.LeftEdge
            if abs(self.mouse_press_pos.x() - self._old_right) < SENSITIVITY:
                self._onResizeDrag = True
                if not self._resizeMode:
                    self._resizeMode = Qt.RightEdge
                else:
                    self._resizeMode |= Qt.RightEdge
            if abs(self.mouse_press_pos.y() - self._old_top) < SENSITIVITY:
                self._onResizeDrag = True
                if not self._resizeMode:
                    self._resizeMode = Qt.TopEdge
                else:
                    self._resizeMode |= Qt.TopEdge
            if abs(self.mouse_press_pos.y() - self._old_bottom) < SENSITIVITY:
                self._onResizeDrag = True
                if not self._resizeMode:
                    self._resizeMode = Qt.BottomEdge
                else:
                    self._resizeMode |= Qt.BottomEdge
            if (not (abs(self.mouse_press_pos.x() - self._old_left) < SENSITIVITY
                or abs(self.mouse_press_pos.x() - self._old_right) < SENSITIVITY
                or abs(self.mouse_press_pos.y() - self._old_top) < SENSITIVITY
                or abs(self.mouse_press_pos.y() - self._old_bottom) < SENSITIVITY)):
                if (realX <= 100 and realY <= 60) \
                    or (realX <= self.width()-170 and realY <= 15) \
                    or (realX <= self.width()-170 and realY >= 45 and realY <= 60):
                    self._onMoveDrag = True
                if realX <= self.calculateLeftWidth() and realY > 60:
                    index = self.calculateLeftIndex(event.position().y())
                    if index >= 0 and index < len(self._menu): # 这里使用 len(self._menu) 是为了允许新建标签页
                        self._onLeftDragIndex = index
                        self.mouse_leftdrag_pos = event.position().toPoint() - QPoint(5, self.calculateLeftY(self._onLeftDragIndex)+5)
                        self._onLeftDrag = True
                    else:
                        self._onLeftDrag = False
            if self.mouse_press_pos.x()-self._old_left <= self.calculateLeftWidth()-30 and self.mouse_press_pos.y()-self._old_top >= 60:
                index = self.calculateLeftIndex(self.mouse_press_pos.y()-self._old_top)
                if index >= 0 and index < len(self._menu): # 这里使用 len(self._menu) 是为了允许新建标签页
                    self._index = index
                    self._configured = True
                    toUpdate = True
                if index >= 0 and index == len(self._menu): # 新建标签页
                    self._index = index
                    self._menu.append(MENU_URL_INDEX[">homepage"](self))
                    self._configured = True
                    toUpdate = True
            if realX >= 100 and realX <= self.width()-170 and realY >= 15 and realY <= 45:
                if not self._focusLocation:
                    toUpdate = True
                self._focusLocation = True
            else:
                if self._focusLocation:
                    toUpdate = True
                self._focusLocation = False
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):

        toUpdate = False
        realX = event.position().x()
        realY = event.position().y()
        if self._leftButtonXBackgroundItem:
            self._scene.removeItem(self._leftButtonXBackgroundItem)
            self._leftButtonXBackgroundItem = None
        if self._onLeftButton:
            if self.mouse_press_pos is None:
                return super().mouseMoveEvent(event)
            self.mouse_now_pos = event.globalPosition().toPoint()
            self.mouse_now_realPos = event.position().toPoint()
            delta = self.mouse_now_pos - self.mouse_press_pos
            if self._onMoveDrag:
                self.mouse_press_pos = self.mouse_now_pos
                self.move(self.pos() + delta)
            if self._onResizeDrag:
                if self._resizeMode == Qt.LeftEdge:
                    self.setGeometry(self._old_left + delta.x(), self._old_top, self._old_width - delta.x(), self._old_height)
                    cursor_shape = Qt.SizeHorCursor
                elif self._resizeMode == Qt.RightEdge:
                    self.setGeometry(self._old_left, self._old_top, self._old_width + delta.x(), self._old_height)
                    cursor_shape = Qt.SizeHorCursor
                elif self._resizeMode == Qt.TopEdge:
                    self.setGeometry(self._old_left, self._old_top + delta.y(), self._old_width, self._old_height - delta.y())
                    cursor_shape = Qt.SizeVerCursor
                elif self._resizeMode == Qt.BottomEdge:
                    self.setGeometry(self._old_left, self._old_top, self._old_width, self._old_height + delta.y())
                    cursor_shape = Qt.SizeVerCursor
                elif self._resizeMode == Qt.LeftEdge | Qt.TopEdge:
                    self.setGeometry(self._old_left + delta.x(), self._old_top + delta.y(), self._old_width - delta.x(), self._old_height - delta.y())
                    cursor_shape = Qt.SizeFDiagCursor
                elif self._resizeMode == Qt.RightEdge | Qt.TopEdge:
                    self.setGeometry(self._old_left, self._old_top + delta.y(), self._old_width + delta.x(), self._old_height - delta.y())
                    cursor_shape = Qt.SizeBDiagCursor
                elif self._resizeMode == Qt.LeftEdge | Qt.BottomEdge:
                    self.setGeometry(self._old_left + delta.x(), self._old_top, self._old_width - delta.x(), self._old_height + delta.y())
                    cursor_shape = Qt.SizeBDiagCursor
                elif self._resizeMode == Qt.RightEdge | Qt.BottomEdge:
                    self.setGeometry(self._old_left, self._old_top, self._old_width + delta.x(), self._old_height + delta.y())
                    cursor_shape = Qt.SizeFDiagCursor
                else:
                    cursor_shape = Qt.ArrowCursor
                QApplication.setOverrideCursor(QCursor(cursor_shape))
            if self._onLeftDrag:
                if realY > 60 and realY < self.height():
                    self._onLeftRealDrag = True
                    index = self.calculateLeftIndex(realY)
                    if index >= 0 and index < len(self._menu):
                        self._onLeftDragToIndex = index
                toUpdate = True
        else:
            if realX < self.calculateLeftWidth():
                index = self.calculateLeftIndex(realY)
                if index >= 0 and index < len(self._menu) and realX > self.calculateLeftWidth()-30 and realX <= self.calculateLeftWidth()-10:
                    self._onLeftHighLightIndex = index
                    self._leftButtonXBackgroundItem = QGraphicsRoundedRectangleItem()
                    self._leftButtonXBackgroundItem.setBrush(QBrush(QColor(MAIN_L2TEXT_COLOR)))
                    self._leftButtonXBackgroundItem.setRadius(RADIUS)
                    self._leftButtonXBackgroundItem.setPos(self.calculateLeftWidth()-30, self.calculateLeftY(index)+10)
                    self._leftButtonXBackgroundItem.setSize(20, 20)
                    self._scene.addItem(self._leftButtonXBackgroundItem)
            moveMode = None
            if realX < SENSITIVITY:
                self._onResizeDrag = True
                if not moveMode:
                    moveMode = Qt.LeftEdge
                else:
                    moveMode |= Qt.LeftEdge
            if realX > self.width()-SENSITIVITY:
                self._onResizeDrag = True
                if not moveMode:
                    moveMode = Qt.RightEdge
                else:
                    moveMode |= Qt.RightEdge
            if realY < SENSITIVITY:
                self._onResizeDrag = True
                if not moveMode:
                    moveMode = Qt.TopEdge
                else:
                    moveMode |= Qt.TopEdge
            if realY > self.height()-SENSITIVITY:
                self._onResizeDrag = True
                if not moveMode:
                    moveMode = Qt.BottomEdge
                else:
                    moveMode |= Qt.BottomEdge
            if moveMode == Qt.LeftEdge:
                cursor_shape = Qt.SizeHorCursor
            elif moveMode == Qt.RightEdge:
                cursor_shape = Qt.SizeHorCursor
            elif moveMode == Qt.TopEdge:
                cursor_shape = Qt.SizeVerCursor
            elif moveMode == Qt.BottomEdge:
                cursor_shape = Qt.SizeVerCursor
            elif moveMode == Qt.LeftEdge | Qt.TopEdge:
                cursor_shape = Qt.SizeFDiagCursor
            elif moveMode == Qt.RightEdge | Qt.TopEdge:
                cursor_shape = Qt.SizeBDiagCursor
            elif moveMode == Qt.LeftEdge | Qt.BottomEdge:
                cursor_shape = Qt.SizeBDiagCursor
            elif moveMode == Qt.RightEdge | Qt.BottomEdge:
                cursor_shape = Qt.SizeFDiagCursor
            else:
                cursor_shape = Qt.ArrowCursor
            QApplication.setOverrideCursor(QCursor(cursor_shape))
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        toUpdate = False
        self._onLeftButton = False
        if event.button() == Qt.LeftButton:
            self._onMoveDrag = False
            self._onResizeDrag = False
            if self.x()+self.width() <= 5 and not self.isFullScreen():
                self.setGeometry(5, self.y(), self.width(), self.height())
                toUpdate = True
            if self.x() >= self.screen().size().width() - 5 and not self.isFullScreen():
                self.setGeometry(self.screen().size().width() - 5, self.y(), self.width(), self.height())
                toUpdate = True
            if self.y() <= 5 and not self.isFullScreen():
                self.setGeometry(self.x(), 5, self.width(), self.height())
                toUpdate = True
            if self.y() >= self.screen().size().height() - 5 and not self.isFullScreen():
                self.setGeometry(self.x(), self.screen().size().height() - 5, self.width(), self.height())
                toUpdate = True
            if self._onLeftDrag and self._onLeftRealDrag:
                self._menu.insert(self._onLeftDragToIndex, self._menu.pop(self._onLeftDragIndex))
                if self._onLeftDragToIndex >= 0 and self._onLeftDragToIndex < len(self._menu):
                    self._index = self._onLeftDragToIndex
                self._configured = True
                toUpdate = True
            self._onLeftDrag = False
            self._onLeftRealDrag = False
            self._onLeftDragIndex = 0
            self._onLeftDragToIndex = 0
            realX = event.position().x()
            realY = event.position().y()
            if realX > self.width() - 45 and realX < self.width() - 20 and realY > 10 and realY < 50: # 关闭
                self.setMinimumSize(1, 1)
                self._closed = True
                toUpdate = True
            if realX > self.width() - 85 and realX < self.width() - 60 and realY > 10 and realY < 50: # 最大化
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()
                toUpdate = True
            if realX > self.width() - 125 and realX < self.width() - 100 and realY > 10 and realY < 50: # 最小化
                self.showMinimized()
                toUpdate = True
            if realX > self.width() - 165 and realX < self.width() - 140 and realY > 10 and realY < 50: # 摘要模式
                self.addMessage(title="功能请求", message="需要完善的功能: 摘要模式", source="self.mouseReleaseEvent")
            if realX >= self.calculateLeftWidth()-30 and realX <= self.calculateLeftWidth()-10 and realY >= self.calculateLeftY(self._onLeftHighLightIndex)+10 and realY <= self.calculateLeftY(self._onLeftHighLightIndex)+30: # 关闭标签页
                if self._index >= self._onLeftHighLightIndex:
                    self._index -= 1
                    if self._index == -1:
                        self._index = 0
                self._menu[self._onLeftHighLightIndex].close()
                del self._menu[self._onLeftHighLightIndex]
                if len(self._menu) == 0:
                    exitProgram()
                if self._onLeftHighLightIndex >= len(self._menu):
                    self._onLeftHighLightIndex = 0
                self._configured = True
                toUpdate = True
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        x = self.calculateLeftWidth()+5
        y = 60
        width = self.calculateRightWidth()
        height = self.height()-65
        ppointf = QPointF(event.position().x()-x, event.position().y()-y)
        if ppointf.x() > 0 and ppointf.y() > 0:
            pevent = QMouseEvent(QEvent.Type.MouseButtonRelease, ppointf, Qt.LeftButton, Qt.NoButton, Qt.NoModifier)
            self._menu[self._index].mouseReleaseEvent(pevent, x, y, width, height)
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        
        position = event.position()
        angle = event.angleDelta()
        toUpdate = False
        if position.x() < self.calculateLeftWidth() and position.y() > 60:
            self._startY += angle.y() / 5
            if self._startY > 60:
                self._startY = 60
            if self.calculateLeftY(len(self._menu)-1) < 60:
                self._startY -= angle.y() / 5
            self._configured = True
            toUpdate = True
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
    
    def resizeEvent(self, event):

        self._configured = True
        self._chunk = CHUNK
        self._timer.setInterval(0)
        self._pageTimer.setInterval(0)
        self._scene.setSceneRect(0, 0, self.width(), self.height())
        self.setSceneRect(0, 0, self.width(), self.height())
    
    def keyPressEvent(self, event):

        toUpdate = False
        if self._focusLocation:
            key = event.key()
            if key == ESC:
                self._focusLocation = False
            elif key == RETURN or key == LITTLE_RETURN:
                try:
                    if self._location[0] != ">":
                        self._location = ">" + self._location
                    self._menu[self._index].close()
                    self._menu[self._index] = MENU_URL_INDEX[self._location](self)
                    self._location = ""
                    self._configured = True
                except KeyError as msg:
                    self.addMessage(title="错误", message="输入的地址无效: %s"%self._location, source="self.keyPressEvent")
                    self._location = ""
                    self.addMessage(title="功能请求", message="自动纠正, 模糊查找", source="self.keyPressEvent")
                self._focusLocation = False
            elif key == BACKSPACE:
                self._location = self._location[:-1]
            elif key == 32: # 剔除空格
                pass
            elif key <= 1114111:
                try:
                    self._location += chr(key).lower()
                except:
                    pass
            toUpdate = True
        else:
            self._menu[self._index].keyPressEvent(event)
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
        return super().keyPressEvent(event)
    
    def pageTimer(self):

        self._pageChunk = self._chunk
        for i in self._pageGroup:
            self._scene.removeItem(i)
        self._pageGroup = []
        x = self.calculateLeftWidth()+5
        y = 60
        width = self.calculateRightWidth()
        height = self.height()-65
        self._menu[self._index].repaint(x, y, width, height)
        for i in range(len(self._menu)):
            if i != self._index:
                self._menu[i].background()
        self._pageTimer.setInterval(self._pageChunk)
    
    def messageTimer(self):

        for i in self._messageGroup:
            self._scene.removeItem(i)
        self._messageGroup = []
        x = 5
        y = self.height()-5
        width = self.calculateLeftWidth()-5
        height = 0
        for i in self._messages:
            opacity = 1
            if i[0] <= -2:
                del i
                continue
            if i[0] <= 0:
                opacity = 1 - (abs(i[0]))/5
            item = QGraphicsTextItem() # 消息正文
            item.setPlainText(i[2])
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.setTextWidth(width-10)
            rect = item.boundingRect()
            y -= rect.height()+40+len(i[4])*20
            item.setOpacity(opacity)
            item.setPos(x+5, y+20)
            item.setZValue(400)
            self._scene.addItem(item)
            self._messageGroup.append(item)
            height = rect.height()
            item = QGraphicsTextItem() # 消息标题
            text = i[1]
            item.setPlainText(text)
            item.setDefaultTextColor(QColor(MAIN_LTEXT_COLOR))
            rect = item.boundingRect()
            while rect.width() > width-10:
                text = text[:-1]
                rect = item.boundingRect()
            item.setOpacity(opacity)
            item.setPos(x+5, y+5)
            item.setZValue(350)
            self._scene.addItem(item)
            self._messageGroup.append(item)
            height += item.boundingRect().height()-5
            item = QGraphicsTextItem() # 消息来源
            text = "来源: "+i[3]
            item.setPlainText(text)
            item.setDefaultTextColor(QColor(MAIN_LTEXT_COLOR))
            rect = item.boundingRect()
            while rect.width() > width-10:
                text = text[:-1]
                item.setPlainText(text)
                rect = item.boundingRect()
            item.setOpacity(opacity)
            item.setPos(x+5, y+height)
            item.setZValue(350)
            self._scene.addItem(item)
            self._messageGroup.append(item)
            height += item.boundingRect().height()-5
            for j in i[4]: # 消息操作
                item = QGraphicsTextItem()
                text = j[0]
                item.setPlainText(text)
                item.setDefaultTextColor(QColor(BUTTON_BACKGROUND_COLOR))
                rect = item.boundingRect()
                while rect.width() > width-10:
                    text = text[:-1]
                    item.setPlainText(text)
                    rect = item.boundingRect()
                item.setPos(x+5, y+height)
                item.setZValue(350)
                self._scene.addItem(item)
                self._messageGroup.append(item)
                height += item.boundingRect().height()-5
            item = QGraphicsRoundedRectangleItem() # 消息背景
            item.setBrush(QBrush(MAIN_COLOR))
            effect = QGraphicsDropShadowEffect()
            effect.setColor(Qt.gray)
            effect.setBlurRadius(5)
            effect.setOffset(1, 1)
            item.setGraphicsEffect(effect)
            item.setOpacity(opacity)
            item.setRadius(RADIUS)
            item.setPos(x, y)
            item.setSize(width, height+5)
            item.setZValue(300)
            self._scene.addItem(item)
            self._messageGroup.append(item)
            i[0] -= 0.1
            y -= 5

    def timer(self):

        if self._closed:
            if CLOSE_ANIMATION == 0:
                new_width = self.width()*0.95
                new_height = self.height()*0.95
                center_x = self.x() + self.width() / 2
                center_y = self.y() + self.height() / 2
                new_x = center_x - new_width / 2
                new_y = center_y - new_height / 2
                self.setGeometry(new_x, new_y, new_width, new_height)
                self.setWindowOpacity((40-self._closeCount/2)/100)
                self._closeCount += 1
                if self._closeCount == 40:
                    exitProgram()
            elif CLOSE_ANIMATION == 1:
                if self._closeCount <= 15:
                    new_x = self.x()*1.005
                    new_y = self.y()*0.95
                else:
                    new_x = self.x()*1.005
                    new_y = self.y()*1.15
                self.setGeometry(new_x, new_y, self.width(), self.height())
                self._closeCount += 1
                if new_y > self.screen().size().height():
                    exitProgram()
            elif CLOSE_ANIMATION == 2:
                self.setWindowOpacity((80-self._closeCount*2)/100)
                self._closeCount += 1
                if self._closeCount == 40:
                    exitProgram()
            else:
                exitProgram()
            self.addMessage(title="功能请求", message="需要更改的动画 应当使用系统时间戳而不是帧时间戳", source="self.timer")

        if self._configured:

            for i in self._group:
                self._scene.removeItem(i)
            self._group = []

            item = QGraphicsRoundedRectangleItem() # 程序背景
            item.setBrush(QBrush(MAIN_BACKGROUND_COLOR))
            item.setRadius(RADIUS)
            item.setPos(0, 0)
            item.setSize(self.width(), self.height())
            self._scene.addItem(item)
            self._group.append(item)

            item = QGraphicsRoundedRectangleItem() # 标签栏背景
            item.setBrush(QBrush(MAIN_CAPTION_COLOR))
            item.setRadius(RADIUS)
            item.setPos(5, 60)
            item.setSize(self.calculateLeftWidth()-5, self.height()-65)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsRoundedRectangleItem() # 标签栏选中高亮
            item.setBrush(QBrush(MAIN_COLOR))
            effect = QGraphicsDropShadowEffect()
            effect.setColor(Qt.gray)
            effect.setBlurRadius(5)
            effect.setOffset(1, 1)
            item.setGraphicsEffect(effect)
            item.setRadius(RADIUS)
            item.setPos(5, 5+self.calculateLeftY(self._index))
            item.setSize(self.calculateLeftWidth()-5, 30)
            self._scene.addItem(item)
            self._group.append(item)
            for i in range(len(self._menu)): # 遍历标签栏
                if self.calculateLeftY(i) < 30:
                    continue
                item = QGraphicsTextItem() # 标签栏文字
                item.setPlainText(self._menu[i].title)
                item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
                item.adjustSize()
                item.setPos(15, 8+self.calculateLeftY(i))
                self._scene.addItem(item)
                self._group.append(item)
                item = QGraphicsTextItem()
                item.setPlainText("✕") # 注: `×` 代表乘号
                item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
                item.setPos(self.calculateLeftWidth()-30, self.calculateLeftY(i)+10)
                item.setZValue(50)
                self._scene.addItem(item)
                self._group.append(item)
            item = QGraphicsTextItem() # 新建标签页
            item.setPlainText("新建标签页")
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.adjustSize()
            item.setPos(15, 8+self.calculateLeftY(len(self._menu)))
            self._scene.addItem(item)
            self._group.append(item)
            if self.calculateLeftY(0) < 60: # 向上
                item = QGraphicsRoundedRectangleItem()
                item.setBrush(QBrush(MAIN_COLOR))
                item.setRadius(RADIUS)
                item.setPos(self.calculateLeftWidth()/2-20, 60)
                item.setSize(40, 20)
                self._scene.addItem(item)
                self._group.append(item)
                item = QGraphicsTextItem()
                item.setPlainText("↑")
                item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
                item.setPos(self.calculateLeftWidth()/2-8, 60)
                self._scene.addItem(item)
                self._group.append(item)
            if self.calculateLeftY(len(self._menu)) > self.height(): # 向下
                item = QGraphicsRoundedRectangleItem()
                item.setBrush(QBrush(MAIN_COLOR))
                item.setRadius(RADIUS)
                item.setPos(self.calculateLeftWidth()/2-20, self.height()-20)
                item.setSize(40, 20)
                self._scene.addItem(item)
                self._group.append(item)
                item = QGraphicsTextItem()
                item.setPlainText("↓")
                item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
                item.setPos(self.calculateLeftWidth()/2-8, self.height()-20)
                self._scene.addItem(item)
                self._group.append(item)

            item = QGraphicsRoundedRectangleItem() # 标题栏背景
            item.setBrush(QBrush(MAIN_CAPTION_COLOR))
            item.setRadius(RADIUS)
            item.setPos(5, 5)
            item.setSize(self.width()-10, 50)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsTextItem() # 标题
            item.setPlainText("桌面")
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.setPos(20, 20)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsRoundedRectangleItem() # 地址栏
            item.setBrush(QBrush(MAIN_COLOR))
            item.setRadius(RADIUS)
            item.setPos(100, 15)
            item.setSize(self.width()-270, 30)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsTextItem() # 摘要按钮
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.setPlainText("⇱")
            item.setFont(QFont("微软雅黑", 14))
            item.setPos(self.width()-160, 15)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsTextItem() # 最小化按钮
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.setPlainText("−")
            item.setFont(QFont("微软雅黑", 14))
            item.setPos(self.width()-120, 15)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsTextItem() # 最大化按钮
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.setPlainText("□")
            item.setFont(QFont("微软雅黑", 14))
            item.setPos(self.width()-80, 15)
            self._scene.addItem(item)
            self._group.append(item)
            item = QGraphicsTextItem() # 关闭按钮
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.setPlainText("×")
            item.setFont(QFont("微软雅黑", 14))
            item.setPos(self.width()-40, 15)
            self._scene.addItem(item)
            self._group.append(item)

            item = QGraphicsRoundedRectangleItem() # 主页面背景
            item.setBrush(QBrush(MAIN_COLOR))
            item.setRadius(RADIUS)
            item.setPos(self.calculateLeftWidth()+5, 60)
            item.setSize(self.calculateRightWidth(), self.height()-65)
            self._scene.addItem(item)
            self._group.append(item)

            self._configured = False

        for i in self._mainGroup:
            self._scene.removeItem(i)
        self._mainGroup = []
        if self._focusLocation:
            item = QGraphicsRoundedRectangleItem() # 地址栏
            item.setPenDefault(QPen(BUTTON_BACKGROUND_COLOR))
            item.setBrush(Qt.NoBrush)
            item.setRadius(RADIUS)
            item.setPos(100, 15)
            item.setSize(self.width()-270, 30)
            self._scene.addItem(item)
            self._mainGroup.append(item)
        item = QGraphicsTextItem() # 地址
        if self._location == "":
            item.setPlainText(self._menu[self._index].location)
            item.setDefaultTextColor(QColor(Qt.gray))
        else:
            item.setPlainText(self._location)
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
        item.setPos(110, 20)
        self._scene.addItem(item)
        self._mainGroup.append(item)

        if self._onLeftDrag and self._onLeftRealDrag: # 拖动
            current = self.mouse_now_realPos - self.mouse_leftdrag_pos
            item = QGraphicsRoundedRectangleItem()
            item.setBrush(QBrush(MAIN_COLOR))
            effect = QGraphicsDropShadowEffect()
            effect.setColor(Qt.gray)
            effect.setBlurRadius(5)
            effect.setOffset(1, 1)
            item.setGraphicsEffect(effect)
            item.setOpacity(0.6)
            item.setRadius(RADIUS)
            item.setPos(current)
            item.setSize(self.calculateLeftWidth()-5, 30)
            item.setZValue(200)
            self._scene.addItem(item)
            self._mainGroup.append(item)
            item = QGraphicsTextItem() # 拖动文字
            item.setPlainText(self._menu[self._onLeftDragIndex].title)
            item.setDefaultTextColor(QColor(MAIN_TEXT_COLOR))
            item.adjustSize()
            item.setOpacity(0.6)
            item.setPos(current.x()+10, current.y()+3)
            item.setZValue(200)
            self._scene.addItem(item)
            self._mainGroup.append(item)

        if not self._onLeftDrag and not self._onResizeDrag:
            self._chunk = int(self._chunk*CHUNK_PERCENT)
            if self._chunk > MAX_CHUNK:
                self._chunk = MAX_CHUNK
        self._timer.setInterval(self._chunk)
        # print(self._chunk)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
