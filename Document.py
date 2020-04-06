
from LineItem import LineType, DeriveLineItem, AssLineItem
import ClsItem

class Document(object):
    clsItems=[]
    lnItems=[]
    canvas=None

    @classmethod
    def get_cls_fromids(cls, ids):
        for id in ids:
            for clsItem in cls.clsItems:
                if clsItem.isMine(id):
                    return clsItem
        return None

    @classmethod
    def remove_line(cls, lnitem):
        if lnitem in Document.lnItems:
            cls.lnItems.remove(lnitem)

    @classmethod
    def add_cls(cls, clsitem):
        cls.clsItems.append(clsitem)

    @classmethod
    def remove_cls(cls, clsitem):
        if clsitem in Document.clsItems:
            cls.clsItems.remove(clsitem)

    @classmethod
    def create_clsitem(cls, clsName, pos):
        item = ClsItem.ClsItem(cls.canvas, clsName, pos)
        cls.add_cls(item)
        return item

    @classmethod
    def createLineItem(cls, line_type, x1, y1, x2, y2):
        if line_type == LineType.derive:
            return DeriveLineItem(cls.canvas, x1, y1, x2, y2)
        elif line_type == LineType.ass:
            return AssLineItem(cls.canvas, x1, y1, x2, y2)
        else:
            return None

    @classmethod
    def createLink(cls, srcCls, dstCls, linkLine):
        srcCls.addOutLns(linkLine)
        dstCls.addInLns(linkLine)
        linkLine.setSrc(srcCls)
        linkLine.setDst(dstCls)
        # 重置连接线端点
        linkLine.on_srcordst_moved()
        cls.lnItems.append(linkLine)

    @classmethod
    def save(cls):
        f = open('classcharm.txt', 'w')
        f.write('@类名:x,y\n')
        for clsitem in cls.clsItems:
            x, y = clsitem.getPos()
            f.write('%s:%s,%s\n' % (clsitem.getName(), x, y))

        f.write('@关系:首-末\n')
        for line in cls.lnItems:
            f.write('%s:%s-%s\n' % (line.type().value, line.src.getName(), line.dst.getName()))
        f.flush()
        f.close()

    @classmethod
    def open(cls):
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
                clsname_item[clsName]=cls.create_clsitem(clsName, (x, y))
            elif contentType==2:
                strs=i.split(':')
                lt=LineType(int(strs[0]))
                strCls=strs[1].split('-')
                srcCls=clsname_item[strCls[0]]
                dstCls=clsname_item[strCls[1]]
                startPos=srcCls.getAnchor()
                endPos=dstCls.getAnchor()
                lnItem =cls.createLineItem(LineType(lt), startPos[0], startPos[1],endPos[0],endPos[1])
                cls.createLink(srcCls, dstCls, lnItem)
        f.close()

    @classmethod
    def save_attrs(cls):
        f = open('classattr.txt', 'w')
        f.write('@类名,属性名,类型,大小\n')
        for clsitem in cls.clsItems:
            for attr in clsitem.get_attrs():
                f.write('%s,%s,%s,%s\n' % (clsitem.getName(), attr[0], attr[1], attr[2]))
        f.flush()
        f.close()

    @classmethod
    def open_attrs(cls):
        f = open('classattr.txt', 'r')
        content = f.readlines()
        i = 0
        for line in content:
            if i > 0: # 实际内容
                line = line.strip('\n')
                strs = line.split(',')
                clsname=strs[0]
                attr=[strs[1], strs[2], strs[3]]
                for clsitem in cls.clsItems:
                    if clsitem.getName() == clsname:
                        clsitem.add_attr(attr)
                        break
            i += 1
        f.close()
