from tkinter import *
from tkinter import ttk

from CurrState import *
import AttrEditor

# 类的图元
class ClsItem(object):

    def __init__(self, Canvas, clsName, position):
        self.attrs = []
        self.__outLns = []  # 以本图元为起始的连接线
        self.__inLins = []  # 以本图元为终止的连接线
        self.__canvas=Canvas
        self.__txt = self.__canvas.create_text(position,text=clsName,fill='green',width=80,activefill='red')
        (x1,y1,x2,y2)=self.__canvas.bbox(self.__txt)
        self.__rect=self.__canvas.create_rectangle(x1-2,y1-2,x2+2,y2+2,fill='white',activefill='red')
        self.__canvas.lift(self.__txt)
        Canvas.tag_bind(self.__txt, "<B1-Motion>",self.onMove)
        Canvas.tag_bind(self.__txt, "<Double-Button-1>",self.on_edit_attr)

    def isMine(self,itemId):
        return itemId==self.__txt or itemId==self.__rect

    def getAnchor(self):
        (x1, y1, x2, y2) = self.__canvas.bbox(self.__rect)
        return (x1 + (x2 - x1) / 2), y1

    def getPos(self):
        x1, y1 = self.__canvas.coords(self.__txt)
        return x1, y1

    def getName(self):
        return self.__canvas.itemcget(self.__txt, 'text')

    def addOutLns(self, LineItem):
        self.__outLns.append(LineItem)

    def addInLns(self, LineItem):
        self.__inLins.append(LineItem)

    def onMove(self, event):
        if CurrState.mode == EditMode.select:
            (x1, y1, x2, y2) = self.__canvas.bbox(self.__txt)
            self.__canvas.move(self.__rect, event.x-x1, event.y-y1)
            self.__canvas.move(self.__txt, event.x-x1, event.y-y1)
            # 连接线跟随
            nowAnchor = self.getAnchor()
            for line in self.__inLins:
                line.setEnd(nowAnchor[0], nowAnchor[1])
            for line in self.__outLns:
                line.setStart(nowAnchor[0], nowAnchor[1])

    def on_edit_attr(self, event):
        dlg = AttrEditor.AttrEditor(self.__canvas, self.attrs)
        dlg.grab_set()
