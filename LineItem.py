from abc import abstractmethod
from tkinter import *

class LineType(enum.Enum):
    invalid=0
    derive=1
    ass=2

class BaseLineItem(object):
    def __init__(self, canvas,x1,y1,x2,y2,color,arrow):
        self.__canvas=canvas
        self.__lineId=self.__canvas.create_line(x1,y1,x2,y2,fill=color,arrow=arrow)

    def setSrc(self, ClsItem):
        self.src = ClsItem

    def setDst(self, ClsItem):
        self.dst = ClsItem

    @abstractmethod
    def type(self):
        pass

    def setStart(self, x, y):
        (x1,y1,x2,y2) = self.__canvas.coords(self.__lineId)
        self.__canvas.coords(self.__lineId, x, y, x2, y2)

    def setEnd(self, x, y):
        (x1, y1, x2, y2) = self.__canvas.coords(self.__lineId)
        self.__canvas.coords(self.__lineId, x1, y1, x, y)

    def delMe(self):
        self.__canvas.delete(self.__lineId)

    def getItemId(self):
        return self.__lineId

#派生连接线
class DeriveLineItem(BaseLineItem):
    def __init__(self, canvas,x1,y1,x2,y2):
        BaseLineItem.__init__(self, canvas, x1, y1, x2, y2, 'blue', LAST)

    def type(self):
        return LineType.derive

#连接关系线
class AssLineItem(BaseLineItem):
    def __init__(self, canvas,x1,y1,x2,y2):
        BaseLineItem.__init__(self, canvas, x1, y1, x2, y2, 'green', NONE)

    def type(self):
        return LineType.ass