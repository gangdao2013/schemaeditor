
from tkinter import *
from tkinter import ttk


class AttrEditor(Toplevel):
    def __init__(self, master, clsitem):
        Toplevel.__init__(self, master)

        self.clsitem = clsitem
        self.item = None #当前选中的属性行
        self.datatypes = ['short', 'int', 'long long', 'float', 'datetime', 'string']
        self.datasize = [2, 4, 8, 4, 8, 9999]

        self.title("编辑属性")
        self.geometry('800x500')

        frame = ttk.Frame(self)
        Label(frame, text="类名：").pack(side=LEFT, ipadx=5)
        self.name_text = StringVar(value=clsitem.getName())
        Entry(frame, textvariable=self.name_text).pack(side=LEFT, ipadx=5)
        Button(frame, text="修改", command=self.on_modifyname).pack(side=LEFT, ipadx=5)
        frame.pack(side=TOP)

        deriveattrs = clsitem.get_attrs_r(False) #继承属性
        if len(deriveattrs) > 0:
            frame0 = ttk.Frame(self)
            Label(frame0, text="继承属性：").pack(side=LEFT, ipadx=5)
            self.tv0 = ttk.Treeview(frame0, show='headings')
            self.tv0.pack(side=RIGHT, ipadx=5)
            self.filltreeview(self.tv0, deriveattrs)
            frame0.pack(side=TOP, ipady=5)

        frame1 = ttk.Frame(self)
        self.attrs = clsitem.attrs #自身属性
        Label(frame1, text="已有属性：").pack(side=LEFT, ipadx=5)
        self.tv = ttk.Treeview(frame1, show='headings')
        self.tv.pack(side=LEFT, ipadx=5)
        self.filltreeview(self.tv, self.attrs)
        self.tv.bind('<Button-1>', self.on_item_changed)

        self.delBtn = Button(frame1, text="删除", command=self.on_del, state='disabled')
        self.delBtn.pack(side=RIGHT, ipadx=5)
        frame1.pack(side=TOP, ipady=5)

        frame2 = ttk.Frame(self)
        Label(frame2, text="属性名：").pack(side=LEFT, ipadx=5)
        self.xls_text = StringVar(value='')
        Entry(frame2, textvariable=self.xls_text).pack(side=LEFT, ipadx=5)

        Label(frame2, text="类型：").pack(side=LEFT, ipadx=5)
        self.comb_type = ttk.Combobox(frame2, values=self.datatypes)
        self.comb_type.pack(side=LEFT, ipadx=5)
        self.comb_type.current(0)
        self.comb_type.bind('<<ComboboxSelected>>', self.on_type_selected)

        Label(frame2, text="大小：").pack(side=LEFT, ipadx=5)
        self.comb_size = ttk.Combobox(frame2, state='disabled')
        self.comb_size.pack(side=LEFT, ipadx=5)

        self.btn = Button(frame2, text="增加", command=self.on_edit)
        self.btn.pack(side=LEFT, ipadx=5)
        frame2.pack(side=TOP, ipady=5)

    @staticmethod
    def filltreeview(treeview, attrs):
        treeview['columns'] = [0, 1, 2]
        treeview.heading(0, text='属性名')
        treeview.heading(1, text='字段类型')
        treeview.heading(2, text='字段大小')
        treeview.tag_configure('jishu', background='red')
        treeview.tag_configure('oushu', background='orange')
        for i,ele in enumerate(attrs):
            if i % 2 == 0:
                treeview.insert(parent='', index='end', values=ele, tags='oushu')
            else:
                treeview.insert(parent='', index='end', values=ele, tags='jishu')

    def on_modifyname(self):
        priname = self.clsitem.getName()
        content = self.name_text.get()
        if priname != content:
            if len(content) > 0:
                self.clsitem.setname(content)
            else:
                self.name_text.set(priname)

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
            for i, item in enumerate(self.tv.get_children(), row):
                if i % 2 == 0:
                    self.tv.item(item, tags='oushu')
                else:
                    self.tv.item(item, tags='jishu')

    def on_edit(self):
        attrname = self.xls_text.get()
        if len(attrname) > 0:
            val = [attrname, self.comb_type.get(), self.comb_size.get()]
            if self.item is None:
                self.attrs.append(val)
                idx = len(self.attrs) - 1
                if idx % 2 == 0:
                    self.tv.insert(parent='', index='end', values=val, tags='oushu')
                else:
                    self.tv.insert(parent='', index='end', values=val, tags='jishu')
            else:
                row = self.tv.index(self.item)
                self.attrs[row] = val
                self.tv.item(self.item, values=val)

    def on_type_selected(self, event=None):
        if self.comb_type.get() == 'string':
            size=[1]
            for i in range(4, 12):
                size.append((1 << i) - 1)
            self.comb_size.config(values=size, state='normal')
            self.comb_size.current(0)
        else:
            val = '%s' % (self.datasize[self.comb_type.current()])
            self.comb_size.config(values=[val], state='disabled')
            self.comb_size.current(0)

