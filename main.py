#!/usr/bin/python
# -*- coding: UTF-8 -*-
# -*- coding: cp936 -*-
 
import tkinter

from tkinter import *
from ClsItem import *
from LineItem import *
from CurrState import *

class MainWin(object):
    def __init__(self):
        self.root = Tk()
        self.menubar = Menu(self.root, tearoff=True)
        self.currPos=10,10

        self.currLn=None
        self.startCls=None

        self.clsItems=[]
        self.lnItems=[]

        self.cv = Canvas(self.root, width=1000, height=500, background='white')
        self.cv.pack()
        openbn = Button(self.root, text='打开', command=self.open)
        openbn.pack(side=LEFT, ipadx=10, ipady=5, padx=3)
        savebn = Button(self.root, text='保存', command=self.save)
        savebn.pack(side=LEFT, ipadx=10, ipady=5, padx=3)

        selbn = Button(self.root, text='选择', command=self.onSelect)
        selbn.pack(side=LEFT, ipadx=10, ipady=5, padx=3)

        derivebn = Button(self.root, text='派生', fg='blue', command=self.onDerive)
        derivebn.pack(side=LEFT, ipadx=10, ipady=5, padx=3)

        derivebn = Button(self.root, text='关联', fg='green', command=self.onAss)
        derivebn.pack(side=LEFT, ipadx=10, ipady=5, padx=3)

        self.stateLabel = Label(self.root, text='选择')
        self.stateLabel.pack(side=RIGHT)

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
            self.createClsItem(xls_text.get(), self.currPos)
            dlg.destroy()

        Button(dlg, text="创建", command=on_click).pack()
        dlg.grab_set()

    def onDerive(self):
        CurrState.mode = EditMode.derive
        self.stateLabel['text'] = '派生'

    def onAss(self):
        CurrState.mode = EditMode.ass
        self.stateLabel['text'] = '关联'

    def onSelect(self):
        CurrState.mode = EditMode.select
        self.stateLabel['text'] = '选择'

    def onContextMenu(self, event):
        ids=self.cv.find_overlapping(event.x-1,event.y-1,event.x+1, event.y+1)
        if len(ids)==0:
            self.currPos=event.x, event.y
            self.menubar.post(event.x_root, event.y_root)

    def onLBtnPress(self, event):
        if CurrState.mode == EditMode.select:
            return
        ids=self.cv.find_overlapping(event.x-1,event.y-1,event.x+1, event.y+1)
        for id in ids:
            for clsItem in self.clsItems:
                if clsItem.isMine(id):
                    self.startCls = clsItem
                    return

    def createClsItem(self, clsName, pos):
        item = ClsItem(self.cv, clsName, pos)
        self.clsItems.append(item)
        return item

    def createLineItem(self, x1, y1, x2, y2):
        line_type=LineType.invalid
        if CurrState.mode == EditMode.derive:
            line_type=LineType.derive
        elif CurrState.mode == EditMode.ass:
            line_type=LineType.ass
        return self.__createLineItem(line_type, x1, y1, x2, y2)

    def __createLineItem(self, line_type, x1, y1, x2, y2):
        if line_type == LineType.derive:
            return DeriveLineItem(self.cv, x1, y1, x2, y2)
        elif line_type == LineType.ass:
            return AssLineItem(self.cv, x1, y1, x2, y2)
        else:
            return None

    def createLink(self, srcCls, dstCls, linkLine):
        srcCls.addOutLns(linkLine)
        dstCls.addInLns(linkLine)
        linkLine.setSrc(srcCls)
        linkLine.setDst(dstCls)
        self.lnItems.append(linkLine)

    def onLBtnRelease(self, event):
        if CurrState.mode == EditMode.select:
            return
        if self.startCls != None:
            items = list(self.cv.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1))
            if self.currLn:# 排除当前连接线
                items.remove(self.currLn.getItemId())

            if len(items) == 0: #未连接到图元，删除连接线
                if self.currLn:
                    self.currLn.delMe()
            else:
                for id in items:
                    bFind=False
                    for clsItem in self.clsItems:
                        if clsItem.isMine(id):
                            bFind=True
                            end=clsItem.getAnchor()
                            if self.currLn:
                                self.currLn.setEnd(end[0], end[1])
                            else:
                                start = self.startCls.getAnchor()
                                self.currLn=self.createLineItem(start[0], start[1], end[0], end[1])
                            # 建立链接
                            self.createLink(self.startCls, clsItem, self.currLn)
                            break
                    if bFind:
                        break
        self.currLn=None
        self.startCls=None

    def onLBtnMove(self, event):
        if CurrState.mode == EditMode.select:
            return
        if self.startCls != None:
            global currLn
            if self.currLn:
                self.currLn.setEnd(event.x, event.y)
            else:
                start = self.startCls.getAnchor()
                self.currLn = self.createLineItem(start[0], start[1], event.x, event.y)

    def save(self):
        f = open('classcharm.txt', 'w')
        f.write('@类名:x,y\n')
        for cls in self.clsItems:
            x, y = cls.getPos()
            f.write('%s:%s,%s\n' % (cls.getName(), x, y))

        f.write('@关系:首-末\n')
        for line in self.lnItems:
            f.write('%s:%s-%s\n' % (line.type().value, line.src.getName(), line.dst.getName()))
        f.flush()

    def open(self):
        f = open('classcharm.txt', 'r')
        content = f.readlines()
        contentType = 0
        clsname_item = {}
        for i in content:
            i=i.strip('\n')
            if i.startswith('@类名'):
                contentType=1
            elif i.startswith('@关系'):
                contentType=2
            elif contentType==1:
                strs=i.split(':')
                clsName=strs[0]
                strPos=strs[1].split(',')
                x=float(strPos[0])
                y=float(strPos[1])
                clsname_item[clsName]=self.createClsItem(clsName,(x,y))
            elif contentType==2:
                strs=i.split(':')
                lt=LineType(int(strs[0]))
                strCls=strs[1].split('-')
                srcCls=clsname_item[strCls[0]]
                dstCls=clsname_item[strCls[1]]
                startPos=srcCls.getAnchor()
                endPos=dstCls.getAnchor()
                lnItem =self.__createLineItem(LineType(lt), startPos[0], startPos[1],endPos[0],endPos[1])
                self.createLink(srcCls, dstCls, lnItem)

if __name__ == '__main__':
    CurrState.init()
    MainWin().show()
