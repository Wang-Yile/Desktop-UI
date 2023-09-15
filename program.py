if __name__ == "__main__":
    exit()

import math
import os
import time
from multiprocessing import Process, Value

import cv2
import psutil
from PIL import Image, UnidentifiedImageError
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (QFileDialog, QGraphicsProxyWidget,
                               QGraphicsTextItem, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QVBoxLayout, QWidget)

import expression
import homepage as serviceHomepage
import mediaCenter as serviceMediaCenter
import monitor as serviceMonitor
import stack
from graph import *
from programapi import convertMemory, makeQGraphicsRoundedRectangle
from programcon import *

if __name__ == "__main__": # 用作调试
    from main import MainWindow

__all__ = [
    "HomePage", "Monitor", "MediaCenter", "Calculator"
]

class BaseProgram():

    location = ""

    def __init__(self, parent):

        self.title = ""
        self.parent:MainWindow = parent
    
    def repaint(self, x, y, width, height):
        
        pass

    def mousePressEvent(self, event: QMouseEvent, x, y, width, height):

        pass

    def mouseReleaseEvent(self, event: QMouseEvent, x, y, width, height):

        pass

    def mouseMoveEvent(self, event: QMouseEvent, x, y, width, height):

        pass

    def keyPressEvent(self, event: QKeyEvent):

        pass

    def background(self):

        pass

    def close(self):

        pass

class HomePage(BaseProgram):

    location = ">homepage"

    def __init__(self, parent):

        super().__init__(parent)

        self.title = "主页"

        if not serviceHomepage.IMAGE_THREAD.is_alive() and not serviceHomepage.IMAGE_CONNECTED:
            serviceHomepage.IMAGE_THREAD.start()
    
    def repaint(self, x, y, width, height):

        self.parent._pageChunk = 1000
        if serviceHomepage.IMAGE_CONNECTED and width > 0 and height > 0:
            pixmap = serviceHomepage.BACKGROUND_IMAGE
            item = QGraphicsRoundedRectangleExpandingImageItem()
            item._image = pixmap
            item.setRadius(RADIUS)
            item.setPos(x, y)
            item.setSize(width, height)
            self.parent._scene.addItem(item)
            self.parent._pageGroup.append(item)
        item = QGraphicsTextItem()
        item.setPlainText("版权所有 (C) The European Southern Observatory (ESO) 欧洲南方天文台")
        item.setDefaultTextColor(QColor("#ffffff"))
        item.setFont(QFont("微软雅黑", 8))
        item.setOpacity(0.6)
        item.setPos(x, y+height-20)
        self.parent._scene.addItem(item)
        self.parent._pageGroup.append(item)

class Monitor(BaseProgram):

    location = ">monitor"

    def __init__(self, parent):

        super().__init__(parent)

        self.title = "资源监视器"

        self._monitor_cpu_percent = []
        self._monitor_cpu_chartview = serviceMonitor.CPU_Monitor(psutil.cpu_count())
        self._monitor_cpu_item = self.parent._scene.addWidget(self._monitor_cpu_chartview.chartview)
        self._monitor_cpu_item.setVisible(False)
        self._monitor_memory_info = None

        self.service = serviceMonitor.Monitor_Service()
        self.service.start()
    
    def repaint(self, x, y, width, height):

        self._pageChunk = 1000
        self._monitor_cpu_percent = self.service.cpu.percent
        self._monitor_cpu_chartview.push(self.service.cpu.tot_percent, self.service.cpu.freq[0].current)
        self._monitor_memory_info = self.service.memory
        xx = x
        yy = y+height/2+1
        ww = width/int(width/105)
        hh = 20
        index = 0
        for i in self._monitor_cpu_percent:
            item = makeQGraphicsRoundedRectangle(xx, yy, ww-5, hh, QPen(BUTTON_BACKGROUND_COLOR))
            self.parent._scene.addItem(item)
            self.parent._pageGroup.append(item)
            item = QGraphicsTextItem()
            item.setPlainText("CPU" + str(index) + " " + str(i) + "%")
            item.setTextWidth(ww-15)
            item.setPos(xx+5, yy)
            self.parent._scene.addItem(item)
            self.parent._pageGroup.append(item)
            xx += ww
            index += 1
            if xx+ww > self.parent.width():
                xx = x
                yy += hh+5
        item = makeQGraphicsRoundedRectangle(x, (yy if xx == x else yy+hh+5), width-5, hh*4, QPen(BUTTON_BACKGROUND_COLOR))
        self.parent._scene.addItem(item)
        self.parent._pageGroup.append(item)
        item = QGraphicsTextItem()
        item.setPlainText("内存占用\n总计 \t" + convertMemory(self._monitor_memory_info.total) + 
                          "\n已使用 \t" + convertMemory(self._monitor_memory_info.used) + 
                          "\n未使用 \t" + convertMemory(self._monitor_memory_info.free) + 
                          "\n百分比 \t" + str(self._monitor_memory_info.percent) + " %")
        item.setPos(x, (yy if xx == x else yy+hh+5))
        self.parent._scene.addItem(item)
        self.parent._pageGroup.append(item)
        self._monitor_cpu_item.setVisible(True)
        self._monitor_cpu_item.setPos(x, y)
        self._monitor_cpu_item.setMinimumSize(width, height/2)
        self._monitor_cpu_item.setMaximumSize(width, height/2)
        self._monitor_cpu_item.setZValue(100)
    
    def background(self):

        self._monitor_cpu_item.setVisible(False)
    
    def close(self):

        self._monitor_cpu_item.setVisible(False)
        self.service.flag = False
        while self.service.is_alive():
            time.sleep(0.01)

class MediaCenter(BaseProgram):

    location = ">mediacenter"

    def __init__(self, parent):

        super().__init__(parent)

        self.title = "媒体中心"

        self.startT = Value("d", 0)
        self.pauseV = Value("b", False)
        self.video = None
        self.audio = None
        self.prepared = False
        self.path = ""
        self.now = 0
    
    def repaint(self, x, y, width, height):

        try:
            self.parent._pageChunk = 1000/(self.video.get(5)+10)
        except (AttributeError, cv2.error):
            self.parent._pageChunk = self.parent._chunk
        try:
            if not self.prepared:
                raise AttributeError
            path = self.path
            item = makeQGraphicsRoundedRectangle(x, y, width, height, brush=QBrush("#000000"))
            self.parent._scene.addItem(item)
            self.parent._pageGroup.append(item)
            if path and self.startT.value != 0:
                fps = self.video.get(5)
                item = makeQGraphicsRoundedRectangle(x, y, width, 30, brush=QBrush("#000000"))
                item.setOpacity(0.6)
                item.setZValue(150)
                self.parent._scene.addItem(item)
                self.parent._pageGroup.append(item)
                item = QGraphicsTextItem()
                item.setPlainText(path)
                item.setDefaultTextColor(QColor("#ffffff"))
                item.setOpacity(0.6)
                item.setPos(x+5, y+5)
                item.setZValue(150)
                self.parent._scene.addItem(item)
                self.parent._pageGroup.append(item)
                if self.now > (time.time()-self.startT.value)*fps:
                    frame = self.frame
                else:
                    while self.now < (time.time()-self.startT.value)*fps:
                        ret, frame = self.video.read()
                        if not ret:
                            self.video = cv2.VideoCapture(self.path)
                            continue
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.now += 1
                    self.frame = frame
                    # print(self.now"])
                item = QGraphicsRoundedRectangleImageItem()
                item._image = QPixmap.fromImage(QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1]*3, QImage.Format.Format_RGB888))
                item.setRadius(RADIUS)
                item.setPos(x, y)
                item.setSize(width, height)
                self.parent._scene.addItem(item)
                self.parent._pageGroup.append(item)
        except AttributeError as msg:
            item = makeQGraphicsRoundedRectangle(x+width/2-80, y+height/2-15, 160, 30, brush=QBrush(BUTTON_BACKGROUND_COLOR))
            self.parent._scene.addItem(item)
            self.parent._pageGroup.append(item)
            item = QGraphicsTextItem()
            item.setPlainText("打开媒体文件")
            item.setDefaultTextColor(QColor(BUTTON_FOREGROUND_COLOR))
            item.setPos(x+width/2-40, y+height/2-10)
            self.parent._scene.addItem(item)
            self.parent._pageGroup.append(item)

    def mouseReleaseEvent(self, event, x, y, width, height):

        realX = event.position().x()
        realY = event.position().y()
        try:
            if not self.prepared:
                raise AttributeError
        except AttributeError:
            if realX >= width/2-80 and realX <= width/2+80 and realY >= height/2-15 and realY <= height/2+15:
                filedialog = QFileDialog()
                file = filedialog.getOpenFileName(caption="打开媒体文件", dir="D:\\")
                filename = file[0]
                if filename != "":
                    try:
                        self.video = cv2.VideoCapture(filename)
                        if self.video.get(5) == 0:
                            raise cv2.error("帧数为 0")
                        try:
                            Image.open(filename)
                        except UnidentifiedImageError:
                            pass
                        else:
                            raise cv2.error("这是一张图片, 不允许使用媒体中心打开")
                        self.audio = Process(target=serviceMediaCenter.sound, args=(filename,self.startT, self.pauseV))
                        self.audio.daemon = True
                        self.audio.start()
                        self.path = filename
                        while self.startT.value == 0:
                            time.sleep(0.01)
                        self.now = 0
                        self.prepared = True
                        self.parent.addMessage(title="功能请求", message="需要完善的功能: 把打开视频作为单独的线程", source="self.mouseReleaseEvent")
                    except cv2.error as msg:
                        self.parent.addMessage(title="cv2 错误", message=str(msg), source="mediaCenter", option=[["为什么会出现此错误", ":mediacenter:why_cv2error"]])
                    except PermissionError as msg:
                        self.parent.addMessage(title="权限错误", message=str(msg), source="mediaCenter", option=[["为什么会出现此错误", ":mediacenter:why_permissionerror"]])
    
    def background(self):

        try:
            if not self.prepared:
                raise AttributeError
            fps = self.video.get(5)
            while self.now < (time.time()-self.startT.value)*fps:
                ret, self.frame = self.video.read()
                if not ret:
                    self.video = cv2.VideoCapture(self.path)
                    continue
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.now += 1
        except AttributeError:
            pass

    def close(self):

        if self.audio is not None and self.audio.is_alive():
            os.system(f"taskkill /F /PID {self.audio.pid}")

class Calculator(BaseProgram):

    location = ">calculator"

    sheet = {
        "x²": "^2",
        "√x": "sqrt(",
        "xⁿ": "^",
        "÷": "/",
        "×": "*",
        "mod": "%"
    }

    def __init__(self, parent):

        super().__init__(parent)

        self.title = "计算器"

        self.mode = "normal"

        self.old_x = None
        self.old_y = None
        self.old_width = None
        self.old_height = None

        self.entry = QLineEdit()
        self.entry.setContextMenuPolicy(Qt.NoContextMenu)
        self.entry.setAlignment(Qt.AlignRight)
        self.entry.returnPressed.connect(self.calculate_ans)
        self.entry_item = self.parent._scene.addWidget(self.entry)

        if self.mode == "normal":
            commands = [
                ["(", ")", "C", "←"],
                ["x²", "√x", "xⁿ", "÷"],
                ["7", "8", "9", "×"],
                ["4", "5", "6", "-"],
                ["1", "2", "3", "+"],
                ["0", ".", "mod", "="]
            ]
        else:
            commands = [
                ["错误: 未知的计算器模式"]
            ]

        self.items:list[list[QGraphicsProxyWidget]] = []
        for i in commands:
            self.items.append([])
            for j in i:
                btn = QPushButton(j)
                btn.pressed.connect((lambda: self.btn_clicked()))
                item = self.parent._scene.addWidget(btn)
                item.setZValue(100)
                self.items[-1].append(item)
    
    def btn_clicked(self):

        for i in self.items:
            for item in i:
                widget:QPushButton = item.widget()
                if widget.isDown():
                    text = self.entry.text()
                    wtext = widget.text()
                    if wtext.isdigit():
                        text += wtext
                    elif wtext == "=":
                        text = str(self.calculate_ans())
                    elif wtext == "C":
                        text = ""
                    elif wtext == "←":
                        text = text[:-1]
                    elif Calculator.sheet.get(wtext, "none") != "none":
                        text += Calculator.sheet[wtext]
                    else:
                        text += wtext
                    self.entry.setText(text)
    
    def calculate_ans(self):

        # 参考资料: https://www.luogu.com.cn/problem/P1175
        try:
            ans = str(expression.execute(self.entry.text()))
        except ValueError as msg:
            ans = str(msg)
            # self.parent.addMessage(title="错误", message=str(msg), source="calculator")
        self.entry.setText(ans)
        return ans

    def keyPressEvent(self, event: QKeyEvent):

        key = event.key()
        if not self.entry.hasFocus():
            if key == BACKSPACE:
                self.entry.setText(self.entry.text()[:-1])
            elif key == RETURN or key == LITTLE_RETURN:
                self.calculate_ans()
            else:
                self.entry.setText(self.entry.text()+event.text())

    def repaint(self, x, y, width, height):

        self.entry.setFont(QFont(["Consolas", "微软雅黑"], int(height*0.1)))
        self.entry.setMinimumSize(width-10, height*0.2-10)
        self.entry.setMaximumSize(width-10, height*0.2-10)
        self.entry_item.setPos(x+5, y+5)
        self.entry_item.setVisible(True)
        self.entry_item.setZValue(100)
        if len(self.items) != 0:
            xx = x+5
            yy = y+height*0.2
            ww = (width-5) / len(self.items[0])
            hh = (height*0.8) / len(self.items)
            for i in self.items:
                xx = x+5
                for item in i:
                    item.widget().setFont(QFont("Consolas", int(hh*0.2)))
                    item.setPos(int(xx), int(yy))
                    item.setMinimumSize(int(ww-5), int(hh-5))
                    item.setMaximumSize(int(ww-5), int(hh-5))
                    item.setVisible(True)
                    xx += ww
                yy += hh

    def background(self):

        self.entry_item.setVisible(False)
        for i in self.items:
            for item in i:
                item.setVisible(False)
