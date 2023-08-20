"""
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple
matplotlib
Pillow
opencv-python
pyaudio
psutil
requests
NumPy
PySide6
"""

import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue, Value

import cv2
# import numpy as np
# import matplotlib.font_manager as mfm
# import matplotlib.pyplot as plt
import psutil
import requests
# from matplotlib import mathtext
# import taichi as ti
from PIL import Image, UnidentifiedImageError
from PySide6.QtCore import QPoint, Qt, QTimer, QUrl
from PySide6.QtGui import (QBrush, QColor, QCursor, QFont, QImage, QPainter,
                           QPen, QPixmap)
from PySide6.QtWidgets import (QApplication, QFileDialog,
                               QGraphicsDropShadowEffect, QGraphicsScene,
                               QGraphicsTextItem, QGraphicsView, QLineEdit,
                               QMainWindow)

# import ImageQt
import mediaCenter as serviceMediaCenter
import monitor as serviceMonitor
import window as winEffect
from graph import *

"""
附注 关于 ZValue 的说明
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

if __name__ == "__main__":
    # ti.init(arch=ti.gpu)
    pool = ThreadPoolExecutor(max_workers=4)

    ESC = 16777216
    TAB = 16777217
    BACKSPACE = 16777219
    RETURN = 16777220
    LITTLE_RETURN = 16777221
    INSERT = 16777222
    DELETE = 16777223
    PAUSE = 16777224
    HOME = 16777232
    END = 16777233
    SHIFT = 16777248
    CTRL = 16777249
    WIN = 16777250
    ALT = 16777251
    CAPSLOCK = 16777252
    NUMSLOCK = 16777253
    SCROLLLOCK = 16777254
    F1 = 16777264
    F2 = 16777265
    F3 = 16777266
    F4 = 16777267
    F5 = 16777268
    F6 = 16777269
    F7 = 16777270
    F8 = 16777271
    F9 = 16777272
    F10 = 16777273
    F11 = 16777274
    F12 = 16777275
    RIGHT_ARROW = 16777301

    # MAXIMUM_STAR = 5e3

    # MAIN_COLOR = "#000000"
    MAIN_COLOR = "#ffffff"
    # MAIN_CAPTION_COLOR = "#222222"
    MAIN_CAPTION_COLOR = "#eeeeee"#"#00ff00"
    # MAIN_BACKGROUND_COLOR = "#222222"
    MAIN_BACKGROUND_COLOR = "#dddddd"#"#ff0000"

    BUTTON_BACKGROUND_COLOR = "#336dab"
    BUTTON_FOREGROUND_COLOR = "#ffffff"
    BUTTON_LIGHT_COLOR = "#eeeeee"

    MAIN_TEXT_COLOR = "#ffffff"
    MAIN_TEXT_COLOR = "#000000"
    MAIN_LTEXT_COLOR = "#666666"
    MAIN_L2TEXT_COLOR = "#bbbbbb"

    RADIUS = 5

    CHUNK = 30 # 窗口更新速度(ms) 值越小窗口动画越流畅, 相应的资源占用更多 (默认为 10 [fps:100], 建议为 30 [fps:33.3])
    MAX_CHUNK = 1000 # 窗口前台最长更新间隔(ms), 这用于动态刷新率 (由于 CHUNK_PERCENT 参数存在, 实际间隔可能更长)
    CHUNK_PERCENT = 2 # 动态刷新率的增长速度, 这应当是一个大于1的数
    SENSITIVITY = 8 # 设置窗口缩放灵敏度 值越大越灵敏 (建议为 5~10)

    CLOSE_ANIMATION = -1

    # HOMEPAGE_CRYSTAL_BALL_COLOR = "#523d8f"

    MENU_URL_INDEX = {
        ">homepage": "主页",
        ">monitor": "资源监视器",
        ">calculator": "计算器",
        ">note": "速记",
        ">todo": "待办事项",
        ">datetime": "时间&日期",
        ">weather": "天气",
        ">mediacenter": "媒体中心",
        ">encryption": "数据加密",
        ">decryption": "数据解密",
        ">steganography": "数据隐写",
        ">settings": "设置",
        ">newtab": "新标签页"
    }

    def getImageFromURL():

        img = QImage()
        while img.isNull():
            index = random.randint(0, 23)
            index2 = random.randint(0, 99)
            string = str(index) + str(index2)
            while len(string) < 4:
                string = "0" + string
            url = "https://cdn.eso.org/images/screen/eso%sa.jpg" % string
            res = requests.get(url)
            img = QImage.fromData(res.content)
        return img

    IMAGE_URLS = [
        "eso0934a",
        "eso1625a",
        "eso1250a",
        "eso1208a",
        "eso1119a",
        "eso0925a",
        "eso1723a",
        "eso1031a",
        "eso1031b",
        "eso0650a",
        "eso1006a",
        "eso1422a",
        "eso1233a",
        "potw1119a",
        "eso0926a"
    ]
    IMAGE_CONNECTED = False

    def getImageFromURL2():

        global IMAGE_CONNECTED
        IMAGE_CONNECTED = False
        if 1 == 2:
            IMAGE_CONNECTED = True
            img = QPixmap("background.jpeg")
            return img
        url = random.sample(IMAGE_URLS, 1)[0]
        print("get background image from https://cdn.eso.org/images/screen/%s.jpg" % url)
        url = "https://cdn.eso.org/images/screen/%s.jpg" % url
        t = time.time()
        res = requests.get(url)
        print("connection costs %.3f s" % (time.time()-t))
        img = QPixmap.fromImage(QImage.fromData(res.content))
        IMAGE_CONNECTED = True
        return img

    IMAGE_THREAD = pool.submit(getImageFromURL2)

    BACKGROUND_IMAGE = None

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

renderedLaTeX:dict[str, QPixmap] = {}

# def renderAsLaTeX(latex, usetex=True, dpi=500, fontsize=20):

#     # # https://blog.csdn.net/weixin_53366150/article/details/122942076
#     # plt.figure(figsize=(0.3, 0.3))
#     # plt.text(-0.3, 0.9, latex, fontsize=fontsize, usetex=usetex)
#     # plt.ylim(0, 1)
#     # plt.xlim(0, 6)
#     # plt.axis("off")
#     # plt.savefig(path, dpi=dpi, bbox_inches="tight")
#     # plt.close()
#     try:
#         return renderedLaTeX[latex]
#     except KeyError:
#         pass
#     prop = mfm.FontProperties(family="consolas", size=fontsize, weight="normal")
#     mathtext.math_to_image(latex, "tmp.png", prop=prop, dpi=dpi)
#     renderedLaTeX[latex] = QPixmap.fromImage(QImage("tmp.png"))
#     return renderedLaTeX[latex]

# @ti.func
# def taichiDistance(x1, y1, x2, y2):

#     return ti.sqrt(ti.pow(ti.abs(x1-x2), 2) + ti.pow(ti.abs(y1-y2), 2))

# @ti.kernel
# def taichiCrystalBall(arr:ti.types.ndarray(dtype=ti.int32, ndim=3)):

#     center_x = arr.shape[0] // 2
#     center_y = arr.shape[1] // 2
#     radius = center_x
#     ti.loop_config(serialize=True)
#     for i in range(0, center_x):
#         able = False
#         for j in range(0, center_y):
#             dis = taichiDistance(i, j, center_x, center_y)
#             if able:
#                 arr[i,j,3] = 255
#             elif dis < radius:
#                 arr[i,j,3] = 255
#                 able = True

class MainWindow(QMainWindow):

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

        self._menu = [
            [2, "计算器", ">calculator", {}],
            # [-1, "新标签页", ">newtab", {}]
        ]
        self._startY = 60
        self._index = 0

        self._messages = []
        self.addMessage(5, "欢迎", "Desktop UI 是自由软件，你可以在 GitHub 上查找和获取它的免费更新。", "system", [["了解详情", "https://github.com/Wang-Yile/Desktop-UI"], ["不再提示", "system:no_mention"]])

        self._scene = QGraphicsScene()
        self._scene.setBackgroundBrush(Qt.NoBrush)
        self._view = QGraphicsView()
        self._view.setBackgroundBrush(Qt.NoBrush)
        self._view.mouseMoveEvent = self.mouseMoveEvent
        self._view.mousePressEvent = self.mousePressEvent
        self._view.mouseReleaseEvent = self.mouseReleaseEvent
        self._view.setScene(self._scene)
        self.setCentralWidget(self._view)

        self.setWindowTitle("桌面")
        self.setMinimumSize(600, 600)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setStyleSheet(u"background: rgb(221, 221, 221); border-width: 3px; border-radius: %dpx" % RADIUS)
        color = convertHEX2RGBA(MAIN_BACKGROUND_COLOR)
        self.setStyleSheet(u"background: rgb(%d, %d, %d); border-radius: %dpx" % (color[0], color[1], color[2], RADIUS))
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(10)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)
        # self.setWindowOpacity(0.8)
        self.resize(1280, 720)

        self._monitor_cpu = pool.submit(serviceMonitor.get_cpu_status)
        self._monitor_cpu_percent = []
        self._monitor_cpu_chartview = serviceMonitor.CPU_Monitor(psutil.cpu_count())
        self._monitor_cpu_item = self._scene.addWidget(self._monitor_cpu_chartview.chartview)
        self._monitor_cpu_item.setVisible(False)
        self._monitor_memory = pool.submit(serviceMonitor.get_memory_status)
        self._monitor_memory_info = None

        self._win_effect = winEffect.WindowEffect()
        self._win_effect.addShadowEffect(self.winId())

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
                    self._menu.append([0, "主页", ">homepage", {}])
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
                    cursor_shape = Qt.ArrowCursor
                elif self._resizeMode == Qt.RightEdge | Qt.TopEdge:
                    self.setGeometry(self._old_left, self._old_top + delta.y(), self._old_width + delta.x(), self._old_height - delta.y())
                    cursor_shape = Qt.ArrowCursor
                elif self._resizeMode == Qt.LeftEdge | Qt.BottomEdge:
                    self.setGeometry(self._old_left + delta.x(), self._old_top, self._old_width - delta.x(), self._old_height + delta.y())
                    cursor_shape = Qt.ArrowCursor
                elif self._resizeMode == Qt.RightEdge | Qt.BottomEdge:
                    self.setGeometry(self._old_left, self._old_top, self._old_width + delta.x(), self._old_height + delta.y())
                    cursor_shape = Qt.ArrowCursor
                QApplication.setOverrideCursor(QCursor(cursor_shape))
            if self._onLeftDrag:
                # if self.calculateLeftY(self._onLeftDragIndex)
                # print(delta.y(), event.position().y())
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
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)

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
                del self._menu[self._onLeftHighLightIndex]
                if len(self._menu) == 0:
                    exit()
                if self._onLeftHighLightIndex >= len(self._menu):
                    self._onLeftHighLightIndex = 0
                self._configured = True
                toUpdate = True
            x = self.calculateLeftWidth()+5
            y = 60
            width = self.calculateRightWidth()
            height = self.height()-65
            if self._menu[self._index][0] == 7: # 媒体中心
                try:
                    if not self._menu[self._index][3]["prepared"]:
                        raise KeyError
                except KeyError:
                    if realX >= x+width/2-80 and realX <= x+width/2+80 and realY >= y+height/2-15 and realY <= y+height/2+15:
                        filedialog = QFileDialog()
                        file = filedialog.getOpenFileName(caption="打开媒体文件", dir="D:\\")
                        filename = file[0]
                        if filename != "":
                            try:
                                self._menu[self._index][3]["startT"] = Value("d", 0)
                                self._menu[self._index][3]["pauseV"] = Value("b", False)
                                self._menu[self._index][3]["video"] = cv2.VideoCapture(filename)
                                if self._menu[self._index][3]["video"].get(5) == 0:
                                    raise cv2.error("帧数为 0")
                                try:
                                    Image.open(filename)
                                except UnidentifiedImageError:
                                    pass
                                else:
                                    raise cv2.error("这是一张图片, 不允许使用媒体中心打开")
                                # self._menu[self._index][3]["type"] = "video"
                                self._menu[self._index][3]["audio"] = Process(target=serviceMediaCenter.sound, args=(filename, self._menu[self._index][3]["startT"], self._menu[self._index][3]["pauseV"]))
                                self._menu[self._index][3]["audio"].daemon = True
                                self._menu[self._index][3]["audio"].start()
                                self._menu[self._index][3]["path"] = filename
                                self._menu[self._index][3]["now"] = 0
                                self._menu[self._index][3]["prepared"] = True
                                self.addMessage(title="功能请求", message="需要完善的功能: 把打开视频作为单独的线程", source="self.mouseReleaseEvent")
                            except cv2.error as msg:
                                self.addMessage(title="cv2 错误", message=str(msg), source="mediaCenter", option=[["为什么会出现此错误", ":mediacenter:why_cv2error"]])
                            except PermissionError as msg:
                                self.addMessage(title="权限错误", message=str(msg), source="mediaCenter", option=[["为什么会出现此错误", ":mediacenter:why_permissionerror"]])
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
    
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
        self._view.setSceneRect(0, 0, self.width(), self.height())
    
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
                    lst = list(MENU_URL_INDEX)
                    self._menu[self._index][0] = lst.index(self._location)
                    self._menu[self._index][1] = MENU_URL_INDEX[self._location]
                    self._menu[self._index][2] = self._location
                    self._menu[self._index][3] = {}
                    self._location = ""
                    self._configured = True
                except ValueError as msg:
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
        if toUpdate:
            self._chunk = CHUNK
            self._timer.setInterval(0)
            self._pageTimer.setInterval(0)
    
    def pageTimer(self):

        global BACKGROUND_IMAGE

        self._pageChunk = self._chunk
        for i in self._pageGroup:
            self._scene.removeItem(i)
        self._pageGroup = []
        x = self.calculateLeftWidth()+5
        y = 60
        width = self.calculateRightWidth()
        height = self.height()-65
        self._monitor_cpu_item.setVisible(False)
        if self._menu[self._index][0] == 0: # 主页
            if IMAGE_CONNECTED and BACKGROUND_IMAGE is None:
                BACKGROUND_IMAGE = IMAGE_THREAD.result()
            if IMAGE_CONNECTED and width > 0 and height > 0:
                pixmap = BACKGROUND_IMAGE
                item = QGraphicsRoundedRectangleExpandingImageItem()
                item._image = pixmap
                item.setRadius(RADIUS)
                item.setPos(x, y)
                item.setSize(width, height)
                self._scene.addItem(item)
                self._pageGroup.append(item)
            item = QGraphicsTextItem()
            item.setPlainText("版权所有 (C) The European Southern Observatory (ESO) 欧洲南方天文台")
            item.setDefaultTextColor(QColor("#ffffff"))
            item.setFont(QFont("微软雅黑", 8))
            item.setOpacity(0.6)
            item.setPos(x, y+height-20)
            self._scene.addItem(item)
            self._pageGroup.append(item)
        elif self._menu[self._index][0] == 1: # 资源监视器
            self._pageChunk = 1000
            if self._monitor_cpu.done():
                result = self._monitor_cpu.result()
                self._monitor_cpu_percent = result.percent
                self._monitor_cpu_chartview.push(result.tot_percent, result.freq[0].current)
                self._monitor_cpu = pool.submit(serviceMonitor.get_cpu_status)
            if self._monitor_memory.done():
                self._monitor_memory_info = self._monitor_memory.result()
                self._monitor_memory = pool.submit(serviceMonitor.get_memory_status)
            xx = x
            yy = y+height/2+1
            ww = width/int(width/105)
            hh = 20
            index = 0
            for i in self._monitor_cpu_percent:
                item = QGraphicsRoundedRectangleItem()
                item.setPenDefault(QPen(BUTTON_BACKGROUND_COLOR))
                item.setBrush(Qt.NoBrush)
                item.setRadius(RADIUS)
                item.setPos(xx, yy)
                item.setSize(ww-5, hh)
                self._scene.addItem(item)
                self._pageGroup.append(item)
                item = QGraphicsTextItem()
                item.setPlainText("CPU" + str(index) + " " + str(i) + "%")
                item.setTextWidth(ww-15)
                item.setPos(xx+5, yy)
                self._scene.addItem(item)
                self._pageGroup.append(item)
                xx += ww
                index += 1
                if xx+ww > self.width():
                    xx = x
                    yy += hh+5
            item = QGraphicsRoundedRectangleItem()
            item.setPenDefault(QPen(BUTTON_BACKGROUND_COLOR))
            item.setBrush(Qt.NoBrush)
            item.setRadius(RADIUS)
            item.setPos(x, (yy if xx == x else yy+hh+5))
            item.setSize(width-5, hh*4)
            self._scene.addItem(item)
            self._pageGroup.append(item)
            item = QGraphicsTextItem()
            item.setPlainText("内存占用\n总计 \t" + convertMemory(self._monitor_memory_info.total) + 
                              "\n已使用 \t" + convertMemory(self._monitor_memory_info.used) + 
                              "\n未使用 \t" + convertMemory(self._monitor_memory_info.free) + 
                              "\n百分比 \t" + str(self._monitor_memory_info.percent) + " %")
            item.setPos(x, (yy if xx == x else yy+hh+5))
            self._scene.addItem(item)
            self._pageGroup.append(item)
            self._monitor_cpu_item.setVisible(True)
            self._monitor_cpu_item.setPos(x, y)
            self._monitor_cpu_item.setMinimumSize(width, height/2)
            self._monitor_cpu_item.setMaximumSize(width, height/2)
            self._monitor_cpu_item.setZValue(100)
        elif self._menu[self._index][0] == 2: # 计算器
            try:
                mode = self._menu[self._index][3]["mode"]
            except KeyError:
                self._menu[self._index][3]["mode"] = mode = "normal"
            try:
                mow = self._menu[self._index][3]["mow"]
            except KeyError:
                self._menu[self._index][3]["mow"] = mow = 0
            if mode == "normal": # 标准计算器
                # lst = [
                #     ["$x^2$", "$\\frac{1}{x}$", "$C$", "$\\leftarrow$"],
                #     ["$\\sqrt{x}$", "$\\sqrt[n]{x}$", "$x^n$", "$\\div$"],
                #     ["$7$", "$8$", "$9$", "$\\times$"],
                #     ["$4$", "$5$", "$6$", "$-$"],
                #     ["$1$", "$2$", "$3$", "$+$"],
                #     ["$\\pm$", "$0$", "$.$", "$=$"]
                # ]
                lst = [
                    ["x²", "⅟x", "C", "←"],
                    ["√x", "x√n", "xⁿ", "÷"],
                    ["7", "8", "9", "×"],
                    ["4", "5", "6", "-"],
                    ["1", "2", "3", "+"],
                    ["+/-", "0", ".", "="]
                ]
                item = QGraphicsRoundedRectangleItem()
                item.setBrush(QBrush(BUTTON_LIGHT_COLOR))
                item.setRadius(RADIUS)
                item.setPos(x+5, y+5)
                item.setSize(width-10, height/2)
                self._scene.addItem(item)
                self._pageGroup.append(item)
                xx = x+5
                yy = y+height/2+10
                ww = int(width/4)
                hh = int(height/12)-1
                for i in lst:
                    xx = x+5
                    for j in i:
                        # pixmap = renderAsLaTeX(j)
                        # item = QGraphicsRoundedRectangleImageItem()
                        # item._image = pixmap
                        # item.setRadius(RADIUS)
                        # item.setPos(xx, yy)
                        # item.setSize(ww-5, 30)
                        # self._scene.addItem(item)
                        # self._pageGroup.append(item)
                        item = QGraphicsRoundedRectangleItem()
                        if j == "=":
                            item.setBrush(QBrush(BUTTON_BACKGROUND_COLOR))
                        else:
                            item.setBrush(QBrush(BUTTON_LIGHT_COLOR))
                        item.setRadius(RADIUS)
                        item.setPos(xx, yy)
                        item.setSize(ww-5, hh-5)
                        self._scene.addItem(item)
                        self._pageGroup.append(item)
                        item = QGraphicsTextItem()
                        item.setPlainText(j)
                        item.setFont(QFont("微软雅黑", 14))
                        if j == "=":
                            item.setDefaultTextColor(QColor(BUTTON_FOREGROUND_COLOR))
                        item.setPos(xx+ww/2-item.boundingRect().width()/2, yy+hh/2-15)
                        self._scene.addItem(item)
                        self._pageGroup.append(item)
                        xx += ww
                    yy += hh
        elif self._menu[self._index][0] == 7: # 媒体中心
            try:
                self._pageChunk = 1000/(self._menu[self._index][3]["video"].get(5)+10)
            except (KeyError, cv2.error):
                self._pageChunk = self._chunk
            try:
                if not self._menu[self._index][3]["prepared"]:
                    raise KeyError
                path = self._menu[self._index][3]["path"]
                item = QGraphicsRoundedRectangleItem()
                item.setBrush(QColor("#000000"))
                item.setRadius(RADIUS)
                item.setPos(x, y)
                item.setSize(width, height)
                self._scene.addItem(item)
                self._pageGroup.append(item)
                if path is not None and self._menu[self._index][3]["startT"].value != 0:
                    # self._chunk = fps
                    fps = self._menu[self._index][3]["video"].get(5)
                    item = QGraphicsRoundedRectangleItem()
                    item.setBrush(QColor("#000000"))
                    item.setRadius(RADIUS)
                    item.setOpacity(0.6)
                    item.setPos(x, y)
                    item.setSize(width, 30)
                    item.setZValue(150)
                    self._scene.addItem(item)
                    self._pageGroup.append(item)
                    item = QGraphicsTextItem()
                    item.setPlainText(path)
                    item.setDefaultTextColor(QColor("#ffffff"))
                    item.setOpacity(0.6)
                    item.setPos(x+5, y+5)
                    item.setZValue(150)
                    self._scene.addItem(item)
                    self._pageGroup.append(item)
                    if self._menu[self._index][3]["now"] > (time.time()-self._menu[self._index][3]["startT"].value)*fps:
                        frame = self._menu[self._index][3]["frame"]
                    else:
                        while self._menu[self._index][3]["now"] < (time.time()-self._menu[self._index][3]["startT"].value)*fps:
                            ret, frame = self._menu[self._index][3]["video"].read()
                            if not ret:
                                self._menu[self._index][3]["video"] = cv2.VideoCapture(self._menu[self._index][3]["path"])
                                continue
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            self._menu[self._index][3]["now"] += 1
                        self._menu[self._index][3]["frame"] = frame
                        # print(self._menu[self._index][3]["now"])
                    item = QGraphicsRoundedRectangleImageItem()
                    item._image = QPixmap.fromImage(QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1]*3, QImage.Format.Format_RGB888))
                    item.setRadius(RADIUS)
                    item.setPos(x, y)
                    item.setSize(width, height)
                    self._scene.addItem(item)
                    self._pageGroup.append(item)
            except KeyError as msg:
                item = QGraphicsRoundedRectangleItem()
                item.setBrush(QBrush(BUTTON_BACKGROUND_COLOR))
                item.setPos(x+width/2-80, y+height/2-15)
                item.setRadius(RADIUS)
                item.setSize(160, 30)
                self._scene.addItem(item)
                self._pageGroup.append(item)
                item = QGraphicsTextItem()
                item.setPlainText("打开媒体文件")
                item.setDefaultTextColor(QColor(BUTTON_FOREGROUND_COLOR))
                item.setPos(x+width/2-40, y+height/2-10)
                self._scene.addItem(item)
                self._pageGroup.append(item)
        for i in range(len(self._menu)):
            if i == self._index:
                continue
            if self._menu[i][0] == 7:
                try:
                    # fps=30 测试样本: 《崩坏: 星穹铁道》白露角色 PV
                    # fps=60 测试样本: 《原神》官方网站主页宣传 PV
                    # 初次测试
                    # fps=30 时接近满帧
                    # fps=60 时实际播放约 12 帧
                    # 修改后测试
                    # fps=30 时接近满帧
                    # fps=60 时约20-40帧 **瓶颈转移到生产者进程**
                    if not self._menu[i][3]["prepared"]:
                        raise KeyError
                    fps = self._menu[i][3]["video"].get(5)
                    while self._menu[i][3]["now"] < (time.time()-self._menu[i][3]["startT"].value)*fps:
                        ret, self._menu[i][3]["frame"] = self._menu[i][3]["video"].read()
                        if not ret:
                            self._menu[i][3]["video"] = cv2.VideoCapture(self._menu[i][3]["path"])
                            continue
                        self._menu[i][3]["frame"] = cv2.cvtColor(self._menu[i][3]["frame"], cv2.COLOR_BGR2RGB)
                        self._menu[i][3]["now"] += 1
                except KeyError:
                    pass
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
                    self.hide()
                    pool.shutdown()
                    sys.exit(0)
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
                    self.hide()
                    pool.shutdown()
                    sys.exit(0)
            elif CLOSE_ANIMATION == 2:
                self.setWindowOpacity((80-self._closeCount*2)/100)
                self._closeCount += 1
                if self._closeCount == 40:
                    self.hide()
                    pool.shutdown()
                    sys.exit(0)
            else:
                self.hide()
                pool.shutdown()
                sys.exit(0)
            self.addMessage(title="功能请求", message="需要更改的动画 应当使用系统时间戳而不是帧时间戳", source="self.timer")
            # warnings.warn("需要更改的动画 应当使用系统时间戳而不是帧时间戳")

        if self._configured:

            for i in self._group:
                self._scene.removeItem(i)
            self._group = []

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
                item.setPlainText(self._menu[i][1])
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
            item.setPlainText(self._menu[self._index][2])
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
            item.setPlainText(self._menu[self._onLeftDragIndex][1])
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