#!/usr/bin/python
# -*- coding: UTF-8 -*-
# -*- coding: cp936 -*-
 
import tkinter

from tkinter import *
from ClsItem import *
from LineItem import *
from CurrState import *
from Document import *

class MainWin(object):
    def __init__(self):
        self.root = Tk()
        self.currLn=None
        self.startCls=None

        frame = Frame(self.root)
        openbn = Button(frame, text='打开', command=self.on_open)
        openbn.pack(side=TOP, ipadx=10, ipady=5, pady=3)
        savebn = Button(frame, text='保存', command=self.on_save)
        savebn.pack(side=TOP, ipadx=10, ipady=5, pady=33)

        self.selbn = Button(frame, text='选择', command=self.onSelect)
        self.selbn.pack(side=TOP, ipadx=10, ipady=5, pady=3)

        self.derivebn = Button(frame, text='派生', fg='blue', command=self.onDerive)
        self.derivebn.pack(side=TOP, ipadx=10, ipady=5, pady=3)

        self.assbn = Button(frame, text='关联', fg='green', command=self.onAss)
        self.assbn.pack(side=TOP, ipadx=10, ipady=5, pady=3)

        frame.pack(side=LEFT, expand=FALSE)

        self.cv = Canvas(self.root, width=1000, height=500, background='white')
        Document.canvas = self.cv
        self.cv.pack(side=RIGHT, fill=BOTH, expand=TRUE)

        self.menubar = Menu(self.root, tearoff=True)
        self.currPos=10,10
        self.menubar.add_command(label='新增', command=self.createClass)
        # 画布与鼠标左键进行绑定
        self.cv.bind_all("<Button-3>", self.onContextMenu)
        self.cv.bind_all("<ButtonPress-1>", self.onLBtnPress)
        self.cv.bind_all("<B1-Motion>", self.onLBtnMove)
        self.cv.bind_all("<ButtonRelease-1>", self.onLBtnRelease)

    def show(self):
        self.root.mainloop()

    def createClass(self):
        dlg = Toplevel(master=self.cv)
        dlg.title("输入类名")
        dlg.geometry('300x100')

        l1 = Label(dlg, text="类名：")
        l1.pack()
        xls_text = StringVar()
        xls = Entry(dlg, textvariable = xls_text)
        xls_text.set(" ")
        xls.pack()

        def on_click():
            Document.create_clsitem(xls_text.get(), self.currPos)
            dlg.destroy()

        Button(dlg, text="创建", command=on_click).pack()
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

    def onContextMenu(self, event):
        ids=self.cv.find_overlapping(event.x-1,event.y-1,event.x+1, event.y+1)
        if len(ids)==0:
            self.currPos=event.x, event.y
            self.menubar.post(event.x_root, event.y_root)

    def onLBtnPress(self, event):
        if CurrState.mode != EditMode.select:
            ids=self.cv.find_overlapping(event.x-1,event.y-1,event.x+1, event.y+1)
            self.startCls = Document.get_cls_fromids(ids)

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

    def open_attr(self, clsname_item):
        f = open('classattr.txt', 'r')
        content = f.readlines()
        i = 0
        for line in content:
            if i > 0: # 实际内容
                line = line.strip('\n')
                strs = line.split(',')
                cls=strs[0]
                attr=[strs[1], strs[2], strs[3]]
                clsname_item[cls].add_attr(attr)
            i += 1
        f.close()

    def on_open(self):
        Document.open()
        Document.open_attrs()

if __name__ == '__main__':
    CurrState.init()
    MainWin().show()
