# -*- coding: utf-8 -*-

from collections import OrderedDict
from pyexcel_xls import get_data
from operator import itemgetter
import collections
from Document import Document
from LineItem import LineType

class ImportSchema:

    def __init__(self, sourceXlsx=r"schema-1.xlsx"):
        self.sourceFile = sourceXlsx

    def do(self):
        xls_data = get_data(self.sourceFile)
        for sheet_n in xls_data.keys():
            # print(sheet_n, ":", xls_data[sheet_n])
            if sheet_n == '数据库表定义（META_TABLE）':
                self.handleMetaTable(xls_data[sheet_n])
            elif sheet_n == '数据库字段定义(META_TABLE_COLUMN)':
                self.handleField(xls_data[sheet_n])

    def handleMetaTable(self, data):
        data.pop(0)  # 忽略表头
        data.sort(key=itemgetter(0))
        x, y = 120, 100
        hInterval = 50
        vInterval = 0
        for row in data:
            if x > 1400:
                x = 120
                y = y + vInterval + 50
                vInterval = 0
            clsitem = Document.create_clsitem(row[1].strip(), row[0], (x, y))
            w,h = clsitem.get_size()
            x = x + w + hInterval
            if vInterval < h:
                vInterval = h

    def handleField(self, data):
        title = [i.strip() for i in data.pop(0)] # 表头
        bTabId = '表ID号' in title
        dataLenPos = -1
        if bTabId:
            dataLenPos = title.index('数据长度')
        dataType = {'ULongLong': ['long long', '8'],
                    'Float': ['float', '4'],
                    'float': ['float', '4'],
                    'VC(15)': ['STRING', '15'],
                    'VC(31)': ['STRING', '31'],
                    'VC(63)': ['STRING', '63'],
                    'VC(127)': ['STRING', '127'],
                    'VC(255)': ['STRING', '255'],
                    'VC(511)': ['STRING', '511'],
                    'VC(1023)': ['STRING', '1023'],
                    'VC(2047)': ['STRING', '2047'],
                    'INT': ['int', '4'],
                    'Short': ['short', '2'],
                    'N(1)': ['STRING', '1'],
                    'D': ['datetime', '8']}

        cache = collections.defaultdict(list)
        for one in data:
            cache[one[0]].append(one)

        for tab in cache:
            if bTabId:
                clsitem = Document.get_cls_byId(tab)
            else:
                clsitem = Document.get_cls_byname(tab)
            if clsitem is None:
                continue
            for field in cache[tab]:
                attr=['','','','']
                fldNo = 0
                bass = False
                for col in range(len(field)):
                    fldDescAttr = title[col]
                    if fldDescAttr == '列英文名称(COLUMN_NAME_ENG)' or fldDescAttr == '域英文名':
                        attr[0] = field[col]
                    if fldDescAttr == '列序号(COLUMN_NO)' or fldDescAttr == '域内部ID号':
                        attr[3] = int(field[col])
                    elif fldDescAttr == '数据类型(DATATYPE)' or fldDescAttr == '数据类型':
                        if field[col] in dataType.keys():
                            dt = dataType[field[col]]
                            attr[1] = dt[0]
                            attr[2] = dt[1]
                        else:
                            if dataLenPos >= 0:
                                attr[1] = field[col]
                                attr[2] = field[dataLenPos]
                            else:
                                print('表%s的字段%s没有匹配的字段类型%s' % (tab, field[1], field[col]))
                    elif fldDescAttr == '引用表名(R_TABLE_NAME)' or fldDescAttr == '引用表名':
                        refclsitem = None
                        if bTabId:
                            refclsitem = Document.get_cls_byId(field[col])
                        else:
                            refclsitem = Document.get_cls_byname(field[col])
                        if refclsitem is not None:
                            bass = True
                            lnItem = Document.createLineItem(LineType.ass, attr[3])
                            Document.createLink(clsitem, refclsitem, lnItem)                            
                if bass is False:
                    clsitem.add_attr(attr)
