#!/usr/bin/python
# -*- coding: UTF-8 -*-
# -*- coding: cp936 -*-

from ClsItem import *
from LineItem import *
from CurrState import *
from ImportSchema import *

class MainWin(object):
    def __init__(self):
        self.root = Tk()
        self.currLn=None
        self.startCls=None
        self.multi_items=[]

        frame = Frame(self.root)
        openbn = Button(frame, text='打开', command=self.on_open)
        openbn.pack(side=TOP, ipadx=10, ipady=5, pady=3)
        savebn = Button(frame, text='保存', command=self.on_save)
        savebn.pack(side=TOP, ipadx=10, ipady=5, pady=33)
        impbn = Button(frame, text='导入', command=self.on_import)
        impbn.pack(side=TOP, ipadx=10, ipady=5, pady=33)

        self.selbn = Button(frame, text='选择', command=self.onSelect)
        self.selbn.pack(side=TOP, ipadx=10, ipady=5, pady=3)

        self.derivebn = Button(frame, text='派生', fg='blue', command=self.onDerive)
        self.derivebn.pack(side=TOP, ipadx=10, ipady=5, pady=3)

        self.assbn = Button(frame, text='关联', fg='green', command=self.onAss)
        self.assbn.pack(side=TOP, ipadx=10, ipady=5, pady=3)

        frame.pack(side=LEFT, expand=FALSE)

        frame2 = Frame(self.root)
        self.cv = Canvas(frame2, width=1700, height=1200, background='white',scrollregion=(0,0,1600,1500))
        Document.canvas = self.cv

        hbar = Scrollbar(frame2, orient=HORIZONTAL, command=self.cv.xview)
        hbar.pack(side=BOTTOM, fill=X)
        vbar = Scrollbar(frame2, orient=VERTICAL, command=self.cv.yview)
        vbar.pack(side=RIGHT, fill=Y)
        self.cv.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.cv.pack(side=LEFT, fill=BOTH, expand=TRUE)

        frame2.pack(side=LEFT)

        self.onSelect() #默认为选择操作

        self.cv.bind("<ButtonPress-1>", self.onLBtnPress)
        self.cv.bind("<B1-Motion>", self.onLBtnMove)
        self.cv.bind("<ButtonRelease-1>", self.onLBtnRelease)
        self.cv.bind("<Button-3>", self.onContextMenu)
        self.cv.bind("<Control-ButtonPress-1>", self.on_multiselect)

        self.currPos=10,10

    def show(self):
        self.root.mainloop()

    def createClass(self):
        dlg = Toplevel(self.cv)
        dlg.title("输入类名")
        dlg.geometry('300x100')
        Label(dlg, text="类名：").pack(side=LEFT)
        editor = StringVar()
        Entry(dlg, textvariable = editor).pack(side=LEFT)

        def on_click():
            Document.create_clsitem(editor.get(), self.currPos)
            dlg.destroy()

        Button(dlg, text="创建", command=on_click).pack(side=LEFT)
        dlg.grab_set()

    def onDerive(self):
        CurrState.mode = EditMode.derive
        self.selbn['bg'] = 'white'
        self.derivebn['bg'] = 'gray'
        self.assbn['bg'] = 'white'

    def onAss(self):
        CurrState.mode = EditMode.ass
        self.selbn['bg'] = 'white'
        self.derivebn['bg'] = 'white'
        self.assbn['bg'] = 'gray'

    def onSelect(self):
        CurrState.mode = EditMode.select
        self.selbn['bg'] = 'gray'
        self.derivebn['bg'] = 'white'
        self.assbn['bg'] = 'white'
        self.cv.unbind("<ButtonPress-1>")

    def onContextMenu(self, event):
        if len(self.multi_items) > 0: #已选择多个类，可抽象出父类
            menubar = Menu(self.root, tearoff=True)
            menubar.add_command(label='抽象父类', command=self.on_abstract)
            menubar.post(event.x_root, event.y_root)
        else:
            ids = self.cv.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1)
            if len(ids) == 0:  # 空白处创建新类
                self.currPos = event.x, event.y
                menubar = Menu(self.root, tearoff=True)
                menubar.add_command(label='新增', command=self.createClass)
                menubar.post(event.x_root, event.y_root)
            else:
                clsitem = Document.get_cls_fromids(ids)
                if clsitem:
                    clsitem.menubar.post(event.x_root, event.y_root)

    def on_multiselect(self, event):
        if CurrState.mode == EditMode.select:
            ids=self.cv.find_overlapping(event.x-1,event.y-1,event.x+1, event.y+1)
            clsitem = Document.get_cls_fromids(ids)
            if clsitem is not None:
                clsitem.setselected('blue')
                self.multi_items.append(clsitem)

    def on_abstract(self):
        tp = Toplevel(self.cv)
        Label(tp, text='父类名：').pack(side=LEFT)
        sv = StringVar(tp)
        Entry(tp, textvariable=sv).pack(side=LEFT)

        def on_ok():
            itemcount = len(self.multi_items)
            frontitem = self.multi_items[0]
            pos = frontitem.getPos()
            parentitem = Document.create_clsitem(sv.get(), (pos[0] + 150, pos[1]-50))
            parent = frontitem.get_parentcls()
            dstcls = frontitem.get_assdestcls()
            srccls = frontitem.get_asssrccls()
            if itemcount > 1: #至少有2个才需要找出共有属性
                for attr in frontitem.attrs:
                    count = 1
                    for clsitem in self.multi_items[1:]:
                        for tmp in clsitem.attrs:
                            if attr == tmp:
                                count += 1
                                break
                    if count == itemcount:
                        parentitem.attrs.append(attr)
            
                for cls in self.multi_items[1:]:
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
                Document.createLink(parentitem, parent[line], lnItem)
            for line in dstcls.keys():
                lnItem = Document.createLineItem(LineType.ass)
                Document.createLink(parentitem, dstcls[line], lnItem)
            for line in srccls.keys():
                lnItem = Document.createLineItem(LineType.ass)
                Document.createLink(srccls[line], parentitem, lnItem)
                
            for cls in self.multi_items:
                cls.remove_dupattr(parentitem.attrs)
                lnItem = Document.createLineItem(LineType.derive)
                Document.createLink(cls, parentitem, lnItem)          
            
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
                cls.deselected()
                
            self.multi_items.clear()
            tp.destroy()

        btn = Button(tp, text='确定', command=on_ok)
        btn.pack(side=LEFT)
        tp.grab_set()

    def onLBtnPress(self, event):
        if CurrState.mode != EditMode.select:
            ids=self.cv.find_overlapping(event.x-1,event.y-1,event.x+1, event.y+1)
            self.startCls = Document.get_cls_fromids(ids)
        else:
            for clsitem in self.multi_items:
                clsitem.deselected()
            self.multi_items.clear()

    def createLineItem(self, x1, y1, x2, y2):
        line_type=LineType.invalid
        if CurrState.mode == EditMode.derive:
            line_type=LineType.derive
        elif CurrState.mode == EditMode.ass:
            line_type=LineType.ass
        return Document.createLineItem(line_type, x1, y1, x2, y2)

    def onLBtnRelease(self, event):
        if CurrState.mode == EditMode.select:
            return
        if self.startCls and self.currLn:
            ids = list(self.cv.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1))
            ids.remove(self.currLn.getItemId())
            if len(ids) == 0: #未连接到图元，删除连接线
                self.currLn.delMe()
            else:
                dstcls = Document.get_cls_fromids(ids)
                if self.startCls != dstcls: # 建立链接
                    Document.createLink(self.startCls, dstcls, self.currLn)
        self.currLn=None
        self.startCls=None

    def onLBtnMove(self, event):
        if CurrState.mode == EditMode.select:
            return
        if self.startCls is not None:
            if self.currLn:
                self.currLn.on_end_moved(self.startCls, event.x, event.y)
            else:
                start = self.startCls.getAnchor()
                self.currLn = self.createLineItem(start[0], start[1], event.x, event.y)

    def on_save(self):
        Document.save()
        Document.save_attrs()

    def on_open(self):
        Document.open()
        Document.open_attrs()
    def on_import(self):
        ImportSchema().do()

if __name__ == '__main__':
    CurrState.init()
    MainWin().show()
