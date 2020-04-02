
from tkinter import *
from tkinter import ttk


class AttrEditor(Toplevel):
    def __init__(self, master, attrs):
        Toplevel.__init__(self, master)

        self.attrs = attrs

        self.title("编辑属性")
        self.geometry('800x500')

        frame1 = ttk.Frame(self)
        Label(frame1, text="已有属性：").pack(side=LEFT, ipadx=5)
        self.tv = ttk.Treeview(frame1, columns=['0', '1'])
        self.tv.heading('#0', text='属性名')
        self.tv.heading('#1', text='字段类型')
        self. tv.heading('#2', text='字段大小')
        self.tv.pack(side=RIGHT, ipadx=5)
        frame1.pack(side=TOP, ipady=5)

        frame2 = ttk.Frame(self)
        l1 = Label(frame2, text="新属性：")
        l1.pack(side=LEFT, ipadx=5)
        self.xls_text = StringVar()
        xls = Entry(frame2, textvariable=self.xls_text)
        self.xls_text.set(" ")
        xls.pack(side=LEFT, ipadx=5)
        Button(frame2, text="增加", command=self.on_click).pack(side=LEFT, ipadx=5)
        frame2.pack(side=TOP, ipady=5)

        self.show_attrs()

    def show_attrs(self):
        for i in self.attrs:
            self.tv.insert(parent='', index='end', text=i[0], values=[i[1], i[2]])

    def on_click(self):
        val = [self.xls_text.get(), 'int', '32']
        self.attrs.append(val)
        self.tv.insert(parent='', index='end', text=val[0], values=[val[1], val[2]])
