
from tkinter import *
from tkinter import ttk


class AttrEditor(Toplevel):
    def __init__(self, master, attrs, deriveattrs):
        Toplevel.__init__(self, master)

        self.attrs = attrs #自身属性
        self.deriveattrs = deriveattrs #继承属性
        self.item = None #当前选中的属性行

        self.title("编辑属性")
        self.geometry('800x500')

        if len(self.deriveattrs) > 0:
            frame0 = ttk.Frame(self)
            Label(frame0, text="继承属性：").pack(side=LEFT, ipadx=5)
            self.tv0 = ttk.Treeview(frame0, columns=[0, 1, 2], show='headings')
            self.tv0.heading(0, text='属性名')
            self.tv0.heading(1, text='字段类型')
            self. tv0.heading(2, text='字段大小')
            self.tv0.pack(side=RIGHT, ipadx=5)
            frame0.pack(side=TOP, ipady=5)
            for i in self.deriveattrs:
                self.tv0.insert(parent='', index='end', values=i)

        frame1 = ttk.Frame(self)
        Label(frame1, text="已有属性：").pack(side=LEFT, ipadx=5)
        self.tv = ttk.Treeview(frame1, columns=[0, 1, 2], show='headings')
        self.tv.heading(0, text='属性名')
        self.tv.heading(1, text='字段类型')
        self. tv.heading(2, text='字段大小')
        self.tv.pack(side=LEFT, ipadx=5)
        self.delBtn = Button(frame1, text="删除", command=self.on_del, state='disabled')
        self.delBtn.pack(side=RIGHT, ipadx=5)
        frame1.pack(side=TOP, ipady=5)

        frame2 = ttk.Frame(self)
        Label(frame2, text="属性名：").pack(side=LEFT, ipadx=5)
        self.xls_text = StringVar()
        xls = Entry(frame2, textvariable=self.xls_text)
        self.xls_text.set(" ")
        xls.pack(side=LEFT, ipadx=5)

        Label(frame2, text="类型：").pack(side=LEFT, ipadx=5)
        self.comb_type = ttk.Combobox(frame2, values=['int', 'long', 'string'])
        self.comb_type.pack(side=LEFT, ipadx=5)
        self.comb_type.current(0)
        self.comb_type.bind('<<ComboboxSelected>>', self.on_type_selected)

        Label(frame2, text="大小：").pack(side=LEFT, ipadx=5)
        self.comb_size = ttk.Combobox(frame2, state='disabled')
        self.comb_size.pack(side=LEFT, ipadx=5)

        self.btn = Button(frame2, text="增加", command=self.on_edit)
        self.btn.pack(side=LEFT, ipadx=5)
        frame2.pack(side=TOP, ipady=5)

        for i in self.attrs:
            self.tv.insert(parent='', index='end', values=i)
        self.tv.bind('<Button-1>', self.on_item_changed)

    def on_item_changed(self, event):
        item = self.tv.identify_row(event.y)
        if len(item) == 0:
            self.xls_text.set('')
            self.comb_type.set('')
            self.comb_size.set('')
            self.btn['text'] = '增加'
            self.item = None
            self.delBtn['state'] = 'disabled'
        else:
            row = self.tv.index(item)
            col = int(self.tv.identify_column(event.x).strip('#')) - 1
            self.xls_text.set(self.attrs[row][0])
            self.comb_type.set(self.attrs[row][1])
            self.comb_size.set(self.attrs[row][2])
            self.btn['text'] = '修改'
            self.item = item
            self.delBtn['state'] = 'normal'
        self.on_type_selected()

    def on_del(self):
        if self.item is not None:
            row = self.tv.index(self.item)
            self.attrs.pop(row)
            self.tv.delete(self.item)

    def on_edit(self):
        attrname = self.xls_text.get()
        if len(attrname) > 0:
            val = [attrname, self.comb_type.get(), self.comb_size.get()]
            if self.item is None:
                self.attrs.append(val)
                self.tv.insert(parent='', index='end', values=val)
            else:
                row = self.tv.index(self.item)
                self.attrs[row] = val
                self.tv.item(self.item, values=val)

    def on_type_selected(self, event=None):
        if self.comb_type.get() == 'string':
            self.comb_size.config(values=['31', '63', '127'], state='normal')
            self.comb_size.current(0)
        else:
            self.comb_size.config(values=[''], state='disabled')
            self.comb_size.current(0)

