from tkinter import *

# 类间的关联关系
class Association(object):
    data=[]

    def __init__(self, Canvas):
        self.__canvas = Canvas

    def add(self,srcCls,line,dstCls):
        self.data.append((srcCls, line, dstCls))
