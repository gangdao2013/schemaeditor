import copy
from tkinter import *
from tkinter import messagebox

from Document import *
from CurrState import *
import AttrEditor

# 类的图元
from LineItem import LineType


class ClsItem(object):
    def __init__(self, Canvas, clsName, position, clsId):
        self.x, self.y = 0, 0 #鼠标按下位置
        self.attrs = []
        self.__outLns = []  # 以本图元为起始的连接线
        self.__inLins = []  # 以本图元为终止的连接线
        self.__canvas=Canvas
        self.clsId = clsId
        self.__txt = self.__canvas.create_text(position,text=clsName,fill='green', activefill='red')
        (x1,y1,x2,y2)=self.__canvas.bbox(self.__txt)
        self.__rect=self.__canvas.create_rectangle(x1-2,y1-2,x2+2,y2+2,fill='white', outline='black')
        self.__canvas.lift(self.__txt)

        Canvas.tag_bind(self.__txt, "<Enter>", self.on_enter)
        Canvas.tag_bind(self.__txt, "<Leave>", self.on_leave)
        Canvas.tag_bind(self.__txt, "<ButtonPress-1>",self.on_press)
        Canvas.tag_bind(self.__txt, "<B1-Motion>",self.onMove)
        #Canvas.tag_bind(self.__txt, "<Button-3>",
        #                func=lambda event : self.menubar.post(event.x_root, event.y_root))

        self.menubar = Menu(Canvas, tearoff=True)
        self.menubar.add_command(label='编辑属性', command=self.on_edit_attr)
        self.menubar.add_command(label='查找潜在的子类', command=self.on_find_maybechild)
        self.menubar.add_separator()
        self.menubar.add_command(label='克隆', command=self.on_clone)
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

    def getId(self):
        return self.clsId

    def setname(self, newname):
        self.__canvas.itemconfig(self.__txt, text=newname)
        (x1,y1,x2,y2)=self.__canvas.bbox(self.__txt)
        self.__canvas.coords(self.__rect, x1-2,y1-2,x2+2,y2+2)

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

    def on_find_maybechild(self):
        maybecls = Document.find_maybechild(self)
        if len(maybecls) > 0:
            for cls in maybecls:
                cls.setselected('blue')
            answer = False
            if len(self.attrs) == 0:
                answer = messagebox.askyesno('提示', '父类无自身属性，其它类都被判作其子类！\n仍要创建派生关系吗？')
            else:
                answer = messagebox.askyesno('提示', '要创建派生关系吗？')
            if answer:
                parent = maybecls[0].get_parentcls()
                dstcls = maybecls[0].get_assdestcls()
                srccls = maybecls[0].get_asssrccls()
                if len(maybecls) > 1:
                    for cls in maybecls[1:]:
                        parent1 = cls.get_parentcls().values()
                        dstcls1 = cls.get_assdestcls().values()
                        srccls1 = cls.get_asssrccls().values()
                        for line in list(parent):
                            if parent[line] not in parent1:
                                parent.pop(line)
                        for line in list(dstcls):
                            if dstcls[line] not in dstcls1:
                                dstcls.pop(line)
                        for line in list(srccls):
                            if srccls[line] not in srccls1:
                                srccls.pop(line)
                
                for line in parent.keys():
                    lnItem = Document.createLineItem(LineType.derive)
                    Document.createLink(self, parent[line], lnItem)
                for line in dstcls.keys():
                    lnItem = Document.createLineItem(LineType.ass)
                    Document.createLink(self, dstcls[line], lnItem)
                for line in srccls.keys():
                    lnItem = Document.createLineItem(LineType.ass)
                    Document.createLink(srccls[line], self, lnItem)
                        
                for cls in maybecls:
                    cls.remove_dupattr(self.attrs)
                    lnItem = Document.createLineItem(LineType.derive)
                    Document.createLink(cls, self, lnItem)
                    parent1 = cls.get_parentcls()
                    dstcls1 = cls.get_assdestcls()
                    srccls1 = cls.get_asssrccls()
                    for ln in parent.keys():
                        for line in parent1.keys():
                            if parent[ln] == parent1[line]:
                                line.delMe()
                    for ln in dstcls.keys():
                        for line in dstcls1.keys():
                            if dstcls[ln] == dstcls1[line]:
                                line.delMe()
                    for ln in srccls.keys():
                        for line in srccls1.keys():
                            if srccls[ln] == srccls1[line]:
                                line.delMe()

            for cls in maybecls:
                cls.deselected()

    # 判断本类是否可能是clsitem的子类
    def maybe_childof(self, parentitem):
        if self is parentitem or len(self.attrs) < len(parentitem.attrs):
            return False
        else:
            bMaybe = True
            attrs2 = self.attrs[:]
            for attr in parentitem.attrs:
                bFound = False
                for ar in attrs2:
                    if attr == ar:
                        bFound = True
                        attrs2.remove(ar)
                        break
                if not bFound:
                    bMaybe = False
                    break
            return bMaybe

    #删除和父类重复的属性
    def remove_dupattr(self, attrs):
        for attr in attrs:
            for ar in self.attrs:
                if attr == ar:
                    self.attrs.remove(ar)
                    break

    def active(self, color):
        self.__canvas.itemconfig(self.__txt, fill=color)
    def deactive(self):
        self.__canvas.itemconfig(self.__txt, fill='green')

    def setselected(self, color):
        self.__canvas.itemconfig(self.__rect, outline=color)

    def deselected(self):
        self.__canvas.itemconfig(self.__rect, outline='black')

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
        dlg = AttrEditor.AttrEditor(self.__canvas, self)
        dlg.grab_set()

    def on_clone(self):
        #不要重名
        srcname = self.getName() + '-1'
        clsitem = Document.get_cls_byname(srcname)
        i=2
        while clsitem is not None:
            srcname = self.getName() + '-%s' % (i)
            i += 1
            clsitem = Document.get_cls_byname(srcname)
        pos = self.getPos()
        pos = pos[0]+30, pos[1]+30
        newitem = Document.create_clsitem(srcname, pos)
        newitem.attrs = copy.copy(self.attrs)

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

    # 取父类
    def get_parentcls(self):
        parentcls = {}
        for line in self.__outLns:
            if isinstance(line, DeriveLineItem):
                parentcls[line] = line.dst
        return parentcls

    # 取目标关联类
    def get_assdestcls(self):
        dstcls = {}
        for line in self.__outLns:
            if isinstance(line, AssLineItem):
                dstcls[line] = line.dst
        return dstcls

    # 取目标源类
    def get_asssrccls(self):
        srccls = {}
        for line in self.__inLins:
            if isinstance(line, AssLineItem):
                srccls[line] = line.src
        return srccls
