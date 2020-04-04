from abc import abstractmethod
from tkinter import *
import math

class LineType(enum.Enum):
    invalid=0
    derive=1
    ass=2

class BaseLineItem(object):
    def __init__(self, canvas, line_id):
        self.__canvas = canvas
        self.__lineId = line_id

    def setSrc(self, ClsItem):
        self.src = ClsItem

    def setDst(self, ClsItem):
        self.dst = ClsItem

    @abstractmethod
    def type(self):
        pass

    def delMe(self):
        self.__canvas.delete(self.__lineId)

    def getItemId(self):
        return self.__lineId

    # 响应连接关系建立后，源或终的位置变化
    def on_srcordst_moved(self):
        src_pos = self.src.get_anchors()
        dst_pos = self.dst.get_anchors()
        mindistance = 0 # 最短距离
        pos = ()
        for sp in src_pos:
            for dp in dst_pos:
                dist = math.pow(sp[0]-dp[0], 2) + math.pow(sp[1]-dp[1], 2)
                if mindistance == 0:
                    mindistance = dist
                    pos = (sp[0], sp[1], dp[0], dp[1])
                elif dist < mindistance:
                    mindistance = dist
                    pos = (sp[0], sp[1], dp[0], dp[1])
        self.__canvas.coords(self.__lineId, pos[0], pos[1], pos[2], pos[3])

    def on_end_moved(self, src_cls, endx, endy): # 响应连接关系还未建立时的终点变化
        src_pos = src_cls.get_anchors()
        mindistance = 0 # 最短距离
        pos = ()
        for sp in src_pos:
            dist = math.pow(sp[0]-endx, 2) + math.pow(sp[1]-endy, 2)
            if mindistance == 0:
                mindistance = dist
                pos = (sp[0], sp[1])
            elif dist < mindistance:
                mindistance = dist
                pos = (sp[0], sp[1])
        self.__canvas.coords(self.__lineId, pos[0], pos[1], endx, endy)

#派生连接线
class DeriveLineItem(BaseLineItem):
    def __init__(self, canvas,x1,y1,x2,y2):
        #line = canvas.create_line(x1,y1,x2,y2,fill='blue',arrow=LAST)
        line = canvas.create_line(x1,y1,x2,y2,fill='blue', arrow=LAST,
                                  arrowshape=(15, 15, 8), width=3)
        BaseLineItem.__init__(self, canvas, line)

    def type(self):
        return LineType.derive

#连接关系线
class AssLineItem(BaseLineItem):
    def __init__(self, canvas,x1,y1,x2,y2):
        line = canvas.create_line(x1,y1,x2,y2,fill='green', arrow=LAST,
                                  arrowshape=(8, 20, 8), width=3)
        BaseLineItem.__init__(self, canvas, line)

    def type(self):
        return LineType.ass