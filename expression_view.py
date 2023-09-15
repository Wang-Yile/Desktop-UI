import decimal
import sys

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene,
                               QGraphicsView)

import expression
import lib.qt_clipboard as qt_clipboard
from programcon import *


def real_len(content: str, encoding: str = "gbk") -> int:
    real = content.encode(encoding)
    return len(real)
def real_width(content: str, little_char_width: int = 7, big_char_width: int = 12) -> int:
    res = 0
    for i in content:
        if real_len(i) >= 2:
            res += big_char_width
        else:
            res += little_char_width
    return res

class MathNode(QGraphicsItem):

    # MathNode Issue-1: 在输入框第一次删除某个字符时可能会导致短时间的卡顿, 原因未知

    MathFunction = [
        "cos",
        "sin",
        "tan",
        "acos",
        "asin",
        "atan",
        "cosh",
        "sinh",
        "tanh",
        "acosh",
        "asinh",
        "atanh",
        "sqrt",
        "cbrt",
        "curt",
        "log",
        "ln",
        "lg",
        "log2",
        "abs"
    ]

    def __init__(self, parent):

        super().__init__()
        self.parent: MainWidget = parent

        self._color_table = [
            "#ffd010",
            "#3282f6",
            "#ba1cb0"
        ]

        self._onCtrl = False

        self._width = 600
        self._title_height = 20
        self._height = 300
        self._radius = 5

        self._title_brush = QBrush("#dd222222")
        self._brush = QBrush("#dd444444")
        self._text_pen = QPen("#ffffff")
        self._pen = QPen("#ffff00")

        self._title = "Title"
        self._title_align = Qt.AlignCenter

        self._mode = "Calculate"
        # self._char_width = 7
        self._content = "(1/sqrt(5))*(((1+sqrt(5))/2)^%d-((1-sqrt(5))/2)^%d)"%(5,5)
        print(self._content)
            # self._content 不能含有中文字符, 否则会造成显示错误和光标导航错误
            # 显示错误 ( paint ) 解决方案: 将计算宽度的 self._insert*self._char_width 改为 real_len(self._content[:self._insert])*self._char_width
            # 光标导航错误 ( mousePressEvent 和 mouseMoveEvent ) 解决方案: 将计算光标位置的 int((realX-self._start)/self._char_width) 改为:
                # len_now = 0
                # self._insert = 0
                # while self._insert < len(self._content) and len_now < realX-self._start:
                #     len_now += real_width(self._content[self._insert])
                #     self._insert += 1
                #     if self._insert >= len(self._content):
                #         if len_now < realX-self._start:
                #             self._insert += 1
                #         break
                # self._insert -= 1
            # 总体解决思路: 用 O(n) 时间替代 O(1) 时间以获得正确性
        self._start = 0
        self._output = ""
        self._output_start = 0
        self._insert = len(self._content)

        self._showMenu = False
        self._menu = [
            ["<mode>"],
            ["Add Define Function"],
            ["Add Set Variable"],
            ["Add Calculate", "Ctrl-N"],
            "<sep>",
            ["Copy Input", "Ctrl-C"],
            ["Copy Output"],
            ["Paste Input", "Ctrl-V"],
            "<sep>",
            ["Clear"],
            ["Delete Node"]
        ]
        self._menu_width = 250
        self._menu_height = 210
        self._menu_offset = -50
        self._standard_flags = QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable

        self.setFlags(self._standard_flags)
    
    def calculate(self):

        try:
            self._output = expression.execute(self._content)
        except ValueError as msg:
            self._output = str(msg)
        except IndexError as msg:
            self._output = "索引错误 (可能由不规范的算式导致): " + str(msg)
        except decimal.InvalidContext as msg:
            self._output = "非法 decimal 上下文 (可能由不规范的算式导致): " + str(msg)
        except decimal.InvalidOperation as msg:
            self._output = "非法 decimal 运算 (可能由不规范的算式导致): " + str(msg)
        except Exception as msg:
            self._output = "未知错误: " + str(msg)
    
    def run_menu(self, command: str):

        match command:
            case "Add Define Function":
                pass
            case "Add Set Variable":
                pass
            case "Add Calculate":
                pass
            case "Copy Input":
                qt_clipboard.setclipboard_text(self._content)
            case "Copy Output":
                qt_clipboard.setclipboard_text(self._output)
            case "Paste Input":
                try:
                    content = qt_clipboard.getclipboard()
                    if not isinstance(content, str):
                        content = str(content)
                    for i in content:
                        if i == "\r" or i == "\n":
                            raise ValueError
                except:
                    pass
                else:
                    t1 = self._content[:self._insert]
                    t2 = self._content[self._insert:]
                    self._content = "".join([t1, content.lower(), t2])
                    self._insert += len(content)
                self.update()
            case "Clear":
                self._content = ""
                self._insert = 0
                self.update()
            case "Delete Node":
                pass
            case _:
                print(command)
                return False
        return True

    def boundingRect(self):

        if self._showMenu:
            return QRectF(0, 0, max(self._width, self._width+self._menu_offset+self._menu_width), max(self._height, self._title_height/2+5+self._menu_height))
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget):

        # painter.drawRoundedRect(0, 0, self._width, self._height, self._radius, self._radius)

        painter.setFont(QFont(["Consolas", "微软雅黑"]))

        painter.setPen(Qt.NoPen) # 标题栏
        painter.setBrush(self._title_brush)
        painter.drawPie(QRectF(0, 0, self._radius*2, self._radius*2), 90*16, 90*16)
        painter.drawPie(QRectF(self._width-self._radius*2, 0, self._radius*2, self._radius*2), 0*16, 90*16)
        painter.drawRect(QRectF(self._radius, 0, self._width-self._radius*2, self._radius))
        if self._radius < self._title_height:
            painter.drawRect(QRectF(0, self._radius, self._width, self._title_height-self._radius))

        painter.setPen(self._text_pen) # 标题栏文字
        painter.drawText(QRectF(5, 3, self._width-20, self._title_height-6), self._title, self._title_align)
        painter.drawText(QPointF(self._width-15, self._title_height/2), "…")

        painter.setPen(Qt.NoPen) # 背景
        painter.setBrush(self._brush)
        painter.drawPie(QRectF(0, self._height-self._radius*2, self._radius*2, self._radius*2), 180*16, 90*16)
        painter.drawPie(QRectF(self._width-self._radius*2, self._height-self._radius*2, self._radius*2, self._radius*2), -90*16, 90*16)
        painter.drawRect(QRectF(self._radius, self._height-self._radius, self._width-self._radius*2, self._radius))
        painter.drawRect(QRectF(0, self._title_height, self._width, self._height-self._radius-self._title_height))

        # painter.setPen(self._text_pen)
        # painter.setBrush(QBrush("#dddd00")) # 光标所在的数

        painter.setPen(self._text_pen) # 输入框文字
        text_width = real_width(self._content[:self._insert])

        def getIndexOfElementsWithSameAttribute(index: int) -> tuple[int]:

            l = index
            r = index
            case_1 = "()+-*/%^=<>"
            while l >= 0 and l < len(self._content) and index - 1 >= 0 and index - 1 < len(self._content):
                if self._content[index-1] in case_1 and self._content[l] in case_1:
                    l += 1
                    break
                elif self._content[l] == ",":
                    pass
                elif self._content[index-1].isdigit() and self._content[l] == ".":
                    pass
                elif self._content[index-1].isdigit() and self._content[l].isdigit():
                    pass
                elif self._content[index-1].islower() and self._content[l].islower():
                    pass
                else:
                    l += 1
                    break
                l -= 1
            while r >= 0 and r < len(self._content) and index - 1 >= 0 and index - 1 < len(self._content):
                if self._content[index-1] in case_1 and self._content[r] in case_1:
                    r -= 1
                    break
                elif self._content[r] == ",":
                    pass
                elif self._content[index-1].isdigit() and self._content[r] == ".":
                    pass
                elif self._content[index-1].isdigit() and self._content[r].isdigit():
                    pass
                elif self._content[index-1].islower() and self._content[r].islower():
                    pass
                else:
                    r -= 1
                    break
                r += 1
            return l, r

        l, r = getIndexOfElementsWithSameAttribute(self._insert-1)
        xx = 5+self._start
        yy = self._height/2+self._title_height/2-10
        bracket = -1
        bracket_insert = -1
        bracket_lst = []
        to_warn = False
        for i in range(len(self._content)): # 逐字符显示并处理括号
            if (i >= l and i <= r) or (i == self._insert-1 and l >= r):
                painter.setPen(QPen("#44aa44"))
            else:
                painter.setPen(self._text_pen)
            if self._content[i] == "(":
                bracket += 1
                painter.setPen(QPen(self._color_table[bracket%len(self._color_table)]))
            if self._content[i] == ")":
                if bracket > -1:
                    painter.setPen(QPen(self._color_table[bracket%len(self._color_table)]))
                else:
                    bracket = 0
                    to_warn = True
                    painter.setPen(QPen("#ff0000"))
                bracket -= 1
            if i == self._insert - 1:
                bracket_insert = bracket
            bracket_lst.append(bracket) # 存储每个位置的括号层级, 左括号的层级总是比右括号多 1
            width = real_width(self._content[i])
            if xx >= 0 and xx <= self._width-12:
                painter.drawText(QRectF(xx, yy, width, 20), self._content[i], Qt.AlignCenter)
            xx += width
        if bracket != -1 or to_warn: # 如果括号未匹配, 显示警告
            painter.setPen(self._text_pen)
            painter.drawText(QRectF(5, self._title_height+5, self._width-10, 20), "警告: 括号未匹配", Qt.AlignLeft)
        xx = 5+self._start
        yy = self._height/2+self._title_height/2-10
        begin = self._insert - 1
        end = self._insert - 1
        begin_xx = end_xx = text_width
        while begin >= 0 and begin < len(self._content) and bracket_lst[begin] >= bracket_insert:
            begin_xx -= real_width(self._content[begin])
            begin -= 1
        while end >= 0 and end < len(self._content) and bracket_lst[end] >= bracket_insert:
            end_xx += real_width(self._content[end])
            end += 1
        if end == len(self._content) and len(self._content) > 0:
            end_xx -= real_width(self._content[-1])
        painter.setPen(self._text_pen)
        painter.drawLine(QPointF(5+self._start+begin_xx, yy+23), QPointF(5+self._start+end_xx, yy+23))
        painter.drawLine(QPointF(5+self._start+begin_xx, yy+25), QPointF(5+self._start+begin_xx, yy+21))
        painter.drawLine(QPointF(5+self._start+end_xx, yy+25), QPointF(5+self._start+end_xx, yy+21))
        if 5+self._start+begin_xx < 5: # 如果最左端在屏幕外, 显示一个标志
            painter.drawLine(QPointF(3, yy+29), QPointF(6, yy+26))
            painter.drawLine(QPointF(3, yy+29), QPointF(6, yy+32))
            painter.drawLine(QPointF(6, yy+29), QPointF(9, yy+26))
            painter.drawLine(QPointF(6, yy+29), QPointF(9, yy+32))
            painter.setFont(QFont(["Consolas", "微软雅黑"], pointSize=8))
            painter.drawText(QRectF(12, yy+23, 50, 10), "MORE", Qt.AlignLeft)
            painter.setFont(QFont(["Consolas", "微软雅黑"]))
        if 5+self._start+end_xx > self._width - 5: # 如果最右端在屏幕外, 显示一个标志
            painter.drawLine(QPointF(self._width-3, yy+29), QPointF(self._width-6, yy+26))
            painter.drawLine(QPointF(self._width-3, yy+29), QPointF(self._width-6, yy+32))
            painter.drawLine(QPointF(self._width-6, yy+29), QPointF(self._width-9, yy+26))
            painter.drawLine(QPointF(self._width-6, yy+29), QPointF(self._width-9, yy+32))
            painter.setFont(QFont(["Consolas", "微软雅黑"], pointSize=8))
            painter.drawText(QRectF(self._width-60, yy+23, 50, 10), "MORE", Qt.AlignRight)
            painter.setFont(QFont(["Consolas", "微软雅黑"]))

        # painter.drawText(QRectF(5+self._start, self._height/2+self._title_height/2-10, real_width(self._content)+10, 20), self._content, Qt.AlignVCenter)
        painter.setPen(self._text_pen)
        painter.drawText(QRectF(5+self._output_start, self._height-25, real_width(self._output)+10, 20), self._output, Qt.AlignVCenter)
        painter.drawLine(QPointF(5+self._start+text_width-3, yy), QPointF(5+self._start+text_width+3, yy))
        painter.drawLine(QPointF(5+self._start+text_width-3, yy+20), QPointF(5+self._start+text_width+3, yy+20))
        painter.drawLine(QPointF(5+self._start+text_width, yy), QPointF(5+self._start+text_width, yy+20))
        if 5+self._start+text_width < 5: # 如果光标在屏幕最左端外, 显示一个标志
            painter.drawLine(QPointF(3, yy-12), QPointF(5, yy-12))
            painter.drawLine(QPointF(3, yy-5), QPointF(5, yy-5))
            painter.drawLine(QPointF(4, yy-12), QPointF(4, yy-5))
            painter.setFont(QFont(["Consolas", "微软雅黑"], pointSize=8))
            painter.drawText(QRectF(7, yy-15, 50, 10), "INSERT", Qt.AlignLeft)
            painter.setFont(QFont(["Consolas", "微软雅黑"]))
        if 5+self._start+text_width > self._width - 5: # 如果光标在屏幕最右端外, 显示一个标志
            painter.drawLine(QPointF(self._width-3, yy-12), QPointF(self._width-5, yy-12))
            painter.drawLine(QPointF(self._width-3, yy-5), QPointF(self._width-5, yy-5))
            painter.drawLine(QPointF(self._width-4, yy-12), QPointF(self._width-4, yy-5))
            painter.setFont(QFont(["Consolas", "微软雅黑"], pointSize=8))
            painter.drawText(QRectF(self._width-57, yy-15, 50, 10), "INSERT", Qt.AlignRight)
            painter.setFont(QFont(["Consolas", "微软雅黑"]))

        if self.isSelected(): # 选中的边框

            painter.setPen(self._pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(QRectF(-1, -1, self._width+2, self._height+2), self._radius, self._radius)

        if self._showMenu: # 右上角菜单

            self._menu_height = 10
            for i in self._menu:
                if isinstance(i, list):
                    self._menu_height += 20
                else:
                    self._menu_height += 10

            x = self._width+self._menu_offset
            y = self._title_height/2+5
            width = self._menu_width
            height = self._menu_height
            yy = y+5

            painter.setPen(self._pen)
            painter.setBrush(self._brush)
            painter.drawRoundedRect(QRectF(x, y, width, height), self._radius, self._radius)

            painter.setPen(self._text_pen)

            for i in self._menu:
                if isinstance(i, list):
                    if i[0] == "<mode>":
                        text = "Mode: %s" % self._mode
                    else:
                        text = i[0]
                    painter.drawText(QRectF(x+25, yy+3, width-50, 20), text)
                    if len(i) == 2:
                        painter.drawText(QRectF(x+25, yy+3, width-50, 20), i[1], Qt.AlignRight)
                    yy += 20
                elif i == "<sep>":
                    painter.drawLine(QPointF(x, yy+5), QPointF(x+width, yy+5))
                    yy += 10

        if self._insert > 0 and self._insert - 1 < len(self._content) and self._content[self._insert-1].islower(): # 提示

            l, r = getIndexOfElementsWithSameAttribute(self._insert-1)
            width = self._menu_width
            height = int(self._height/2-self._title_height/2-15)
            painter.setPen(self._pen)
            painter.setBrush(self._brush)
            painter.drawRoundedRect(QRectF(5+self._start+text_width, self._height/2-self._title_height/2+30, width, height), self._radius, self._radius)
            if l == self._insert and self._insert < len(self._content):
                real_str = self._content[l]
            else:
                real_str = self._content[l:self._insert]
            lst = []
            for i in MathNode.MathFunction:
                if i.startswith(real_str):
                    lst.append(i)
            oxx = 15+self._start+text_width
            xx = oxx
            yy = self._height/2-self._title_height/2+30
            painter.setPen(self._text_pen)
            for i in lst:
                painter.drawText(QRectF(xx, yy, width-20, 15), i, Qt.AlignVCenter)
                xx += 100
                if xx > oxx+width-20:
                    xx = oxx
                    painter.drawLine(QPointF(oxx-10, yy+20), QPointF(oxx+width-10, yy+20))
                    yy += 20
    
    def mousePressEvent(self, event):

        realX = event.pos().x()
        realY = event.pos().y()

        if self._showMenu and realX > self._width+self._menu_offset and realX < self._width+self._menu_offset+self._menu_width and realY > self._title_height/2+5 and realY < self._title_height/2+5+self._menu_height: # 处理菜单
            self._showMenu = True
            nowY = realY - (self._title_height/2+5)
            yy = 10
            if yy < nowY:
                for i in self._menu:
                    if isinstance(i, list):
                        yy += 20
                        if yy >= nowY:
                            self._showMenu = False if self.run_menu(i[0]) else True
                            break
                    else:
                        yy += 10
                        if yy >= nowY:
                            break
            self.update()
            return super().mousePressEvent(event)

        self._showMenu = False
        if event.button() == Qt.LeftButton:
            if realY < self._title_height:
                if realX <= self._width-20:
                    self.setFlags(self._standard_flags | QGraphicsItem.ItemIsMovable)
                if realX > self._width-20 and realX < self._width:
                    self._showMenu = True
            if realY > self._height/2+self._title_height/2-20 and realY < self._height/2+self._title_height/2+20:
                len_now = 0
                self._insert = 0
                while self._insert < len(self._content) and len_now < realX-self._start:
                    len_now += real_width(self._content[self._insert])
                    self._insert += 1
                    if self._insert >= len(self._content):
                        if len_now < realX-self._start:
                            self._insert += 1
                        break
                self._insert -= 1
                if self._insert < 0:
                    self._insert = 0
                if self._insert > len(self._content):
                    self._insert = len(self._content)
            if realY > self._height - 35:
                qt_clipboard.setclipboard_text(self._output)
        self.update()

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        realX = event.pos().x()
        realY = event.pos().y()

        if event.button() == Qt.NoButton: # 为什么是 NoButton ?
            if realY > self._title_height and realY < self._height:
                len_now = 0
                self._insert = 0
                while self._insert < len(self._content) and len_now < realX-self._start:
                    len_now += real_width(self._content[self._insert])
                    self._insert += 1
                    if self._insert >= len(self._content):
                        if len_now < realX-self._start:
                            self._insert += 1
                        break
                self._insert -= 1
                if self._insert < 0:
                    self._insert = 0
                if self._insert > len(self._content):
                    self._insert = len(self._content)
        self.update()

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        self.setFlags(self._standard_flags)

        return super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):

        realX = event.pos().x()
        realY = event.pos().y()

        angle = event.delta()
        if realY > self._height/2+self._title_height/2-20 and realY < self._height/2+self._title_height/2+20:
            self._start -= angle / 5
            if self._start > 0:
                self._start = 0
            if self._start < -real_width(self._content):
                self._start = -real_width(self._content)
        if realY > self._height-35 and realY < self._height:
            self._output_start -= angle / 5
            if self._output_start > 0:
                self._output_start = 0
            if self._output_start < -real_width(self._output):
                self._output_start = -real_width(self._output)
        self.update()

        return super().wheelEvent(event)
    
    def keyPressEvent(self, event):

        key = event.key()

        if self._onCtrl:
            if key == 67 or key == 99: # Ctrl-C
                self.run_menu("Copy Input")
            elif key == 86 or key == 118: # Ctrl-V
                self.run_menu("Paste Input")
        else:
            if key == LEFT:
                self._insert -= 1
                if self._insert < 0:
                    self._insert = 0
            elif key == RIGHT:
                self._insert += 1
                if self._insert > len(self._content):
                    self._insert = len(self._content)
            elif key == BACKSPACE:
                if self._insert > 0:
                    t1 = self._content[:self._insert-1]
                    t2 = self._content[self._insert:]
                    self._content = t1 + t2
                    self._insert -= 1
            elif key == DELETE:
                if self._insert < len(self._content):
                    t1 = self._content[:self._insert]
                    t2 = self._content[self._insert+1:]
                    self._content = t1 + t2
            elif key == ESC:
                self.clearFocus()
                self.setSelected(False)
            elif key == RETURN or key == LITTLE_RETURN:
                self.calculate()
            elif key == CTRL:
                self._onCtrl = True
            elif (key >= 48 and key <= 57) or (key >= 65 and key <= 90) or (key >= 97 and key <= 122) or (key >= 40 and key <= 47) or (key >= 60 and key <= 62) or key == 32 or key == 33 or key == 37 or key == 94:
                t1 = self._content[:self._insert]
                t2 = self._content[self._insert:]
                self._content = "".join([t1, chr(key).lower(), t2])
                self._insert += 1

        width = real_width(self._content[:self._insert]) # 当光标不在屏幕内时, 移动视角
        while 5+self._start+width < 10:
            self._start += 5
        if self._start > 0:
            self._start = 0
        while 5+self._start+width > self._width-10:
            self._start -= 5
        if self._start < -width:
            self._start = -width
        self.update()

        return super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):

        key = event.key()

        if key == CTRL:
            self._onCtrl = False

        return super().keyReleaseEvent(event)

    def focusOutEvent(self, event):

        self._showMenu = False
        self.update()

        return super().focusOutEvent(event)

class MainWidget(QGraphicsView):
    
    def __init__(self):

        super().__init__()
        self.setScene(QGraphicsScene())

        node = MathNode(self)
        node.setPos(10, 10)
        self.scene().addItem(node)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)
    
    def resizeEvent(self, event):

        self.setSceneRect(0, 0, self.width()-5, self.height()-5)
        self.scene().setSceneRect(0, 0, self.width()-5, self.height()-5)
        return super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.resize(1000, 800)
    window.show()
    app.exec()