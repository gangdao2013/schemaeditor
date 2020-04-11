from tkinter import *
from tkinter import ttk

from Document import *
from CurrState import *
import AttrEditor

# 类的图元
from LineItem import LineType


class ClsItem(object):
    def __init__(self, Canvas, clsName, position):
        self.x, self.y = 0, 0 #鼠标按下位置
        self.attrs = []
        self.__outLns = []  # 以本图元为起始的连接线
        self.__inLins = []  # 以本图元为终止的连接线
        self.__canvas=Canvas
        self.__txt = self.__canvas.create_text(position,text=clsName,fill='green', activefill='red')
        (x1,y1,x2,y2)=self.__canvas.bbox(self.__txt)
        self.__rect=self.__canvas.create_rectangle(x1-2,y1-2,x2+2,y2+2,fill='white', activefill='red')
        self.__canvas.lift(self.__txt)

        Canvas.tag_bind(self.__txt, "<Enter>", self.on_enter)
        Canvas.tag_bind(self.__txt, "<Leave>", self.on_leave)
        Canvas.tag_bind(self.__txt, "<ButtonPress-1>",self.on_press)
        Canvas.tag_bind(self.__txt, "<B1-Motion>",self.onMove)
        Canvas.tag_bind(self.__txt, "<Button-3>",
                        func=lambda event : self.menubar.post(event.x_root, event.y_root))

        self.menubar = Menu(Canvas, tearoff=True)
        self.menubar.add_command(label='编辑属性', command=self.on_edit_attr)
        self.menubar.add_separator()
        self.menubar.add_command(label='删除', command=self.on_del)

    def isMine(self,itemId):
        return itemId==self.__txt or itemId==self.__rect

    def getAnchor(self):
        (x1, y1, x2, y2) = self.__canvas.bbox(self.__rect)
        return (x1 + (x2 - x1) / 2), y1

    def get_anchors(self): #所有可连接点
        (x1, y1, x2, y2) = self.__canvas.bbox(self.__rect)
        top = x1 + (x2 - x1) / 2, y1
        bottom = x1 + (x2 - x1) / 2, y2
        left = x1, y1 + (y2-y1) / 2
        right = x2, y1 + (y2-y1) / 2
        return [top, bottom, left, right]

    def getPos(self):
        x1, y1 = self.__canvas.coords(self.__txt)
        return x1, y1

    def get_size(self):
        (x1, y1, x2, y2) = self.__canvas.bbox(self.__rect)
        return (x2-x1, y2-y1)

    def getName(self):
        return self.__canvas.itemcget(self.__txt, 'text')

    def addOutLns(self, line):
        self.__outLns.append(line)

    def del_outln(self, line):
        if line in self.__outLns:
            self.__outLns.remove(line)

    def addInLns(self, line):
        self.__inLins.append(line)

    def del_inln(self, line):
        if line in self.__inLins:
            self.__inLins.remove(line)

    def on_enter(self, event):
        for line in self.__outLns:
            line.on_enter()
        for line in self.__inLins:
            line.on_enter()
    def on_leave(self, event):
        for line in self.__outLns:
            line.on_leave()
        for line in self.__inLins:
            line.on_leave()

    def active(self, color):
        self.__canvas.itemconfig(self.__txt, fill=color)
    def deactive(self):
        self.__canvas.itemconfig(self.__txt, fill='green')

    def on_press(self, event):
        if CurrState.mode == EditMode.select:
            self.x = event.x
            self.y = event.y

    def onMove(self, event):
        if CurrState.mode == EditMode.select:
            self.__canvas.move(self.__rect, event.x-self.x, event.y-self.y)
            self.__canvas.move(self.__txt, event.x-self.x, event.y-self.y)
            # 连接线跟随
            nowAnchor = self.getAnchor()
            for line in self.__inLins:
                line.on_srcordst_moved()
            for line in self.__outLns:
                line.on_srcordst_moved()
            self.x = event.x
            self.y = event.y

    def on_edit_attr(self):
        dlg = AttrEditor.AttrEditor(self.__canvas, self.attrs, self.get_attrs_r(False))
        dlg.grab_set()

    def on_del(self):
        for line in self.__outLns[:]:
            line.delMe()
        for line in self.__inLins[:]:
            line.delMe()
        Document.remove_cls(self)
        self.__canvas.delete(self.__txt)
        self.__canvas.delete(self.__rect)

    def get_attrs(self): # 获取属性，仅自身属性
        return self.attrs

    def get_attrs_r(self, containself=True): # 获取属性，包括各级父类属性
        attrs=[]
        # 取出父类的属性
        for line in self.__outLns:
            if line.type() is LineType.derive:
                attrs.extend(line.dst.get_attrs_r())
        if containself:
            attrs.extend(self.attrs)
        return attrs

    def add_attr(self, attr):
        self.attrs.append(attr)
