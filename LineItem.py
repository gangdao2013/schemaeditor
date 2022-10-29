from abc import abstractmethod
from tkinter import *
import math
import Document

class LineType(enum.Enum):
    invalid=0
    derive=1
    ass=2

class BaseLineItem(object):
    def __init__(self, canvas, line_id, id):
        self._canvas = canvas
        self._lineId = line_id
        self.src = None
        self.dst = None
        self.id = id

        canvas.tag_bind(self._lineId, "<Enter>", self.on_enter)
        canvas.tag_bind(self._lineId, "<Leave>", self.on_leave)
        canvas.tag_bind(self._lineId, "<Button-3>",
                        func=lambda event : self.menubar.post(event.x_root, event.y_root))
        self.menubar = Menu(canvas, tearoff=True)
        self.menubar.add_command(label='删除', command=self.on_del)

    def setSrc(self, clsItem):
        self.src = clsItem
        return self.src

    def setDst(self, clsItem):
        self.dst = clsItem

    @abstractmethod
    def type(self):
        pass

    def getId(self):
        return self.id

    def on_del(self):
        self.delMe()

    def delMe(self):
        if self.src:
            self.src.del_outln(self)
        if self.dst:
            self.dst.del_inln(self)
        Document.Document.remove_line(self)
        self._canvas.delete(self._lineId)

    def getItemId(self):
        return self._lineId

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
        self._canvas.coords(self._lineId, pos[0], pos[1], pos[2], pos[3])

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
        self._canvas.coords(self._lineId, pos[0], pos[1], endx, endy)

    def on_enter(self, event=None):
        self._canvas.itemconfig(self._lineId, fill='red')
        if self.src:
            self.src.active('red')
        if self.dst:
            self.dst.active('red')

    def on_leave(self, event=None):
        self._canvas.itemconfig(self._lineId, fill=self.color())
        if self.src:
            self.src.deactive()
        if self.dst:
            self.dst.deactive()

    @abstractmethod
    def color(self):
        pass

#派生连接线
class DeriveLineItem(BaseLineItem):
    def __init__(self, canvas, id, x1,y1,x2,y2):
        line = canvas.create_line(x1,y1,x2,y2,fill=self.color(), arrow=LAST,
                                  arrowshape=(15, 15, 8), width=1)
        BaseLineItem.__init__(self, canvas, line, id)

    def type(self):
        return LineType.derive

    def color(self):
        return 'blue'

#连接关系线
class AssLineItem(BaseLineItem):
    def __init__(self, canvas, id, x1,y1,x2,y2):
        line = canvas.create_line(x1,y1,x2,y2,fill=self.color(), arrow=LAST,
                                  arrowshape=(8, 20, 8), width=1)
        BaseLineItem.__init__(self, canvas, line, id)

    def type(self):
        return LineType.ass

    def color(self):
        return 'green'