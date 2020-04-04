
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
        self.tv = ttk.Treeview(frame1, columns=[0, 1, 2], show='headings')
        self.tv.heading(0, text='属性名')
        self.tv.heading(1, text='字段类型')
        self. tv.heading(2, text='字段大小')
        self.tv.pack(side=RIGHT, ipadx=5)
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

        Button(frame2, text="增加", command=self.on_add).pack(side=LEFT, ipadx=5)
        frame2.pack(side=TOP, ipady=5)

        self.show_attrs()

    def show_attrs(self):
        for i in self.attrs:
            self.tv.insert(parent='', index='end', values=i)

    def on_add(self):
        val = [self.xls_text.get(), self.comb_type.get(), self.comb_size.get()]
        self.attrs.append(val)
        self.tv.insert(parent='', index='end', values=val)

    def on_type_selected(self, event):
        if self.comb_type.get() == 'string':
            self.comb_size.config(values=['31', '63', '127'], state='normal')
            self.comb_size.current(0)
        else:
            self.comb_size.config(values=[''], state='disabled')
            self.comb_size.current(0)

