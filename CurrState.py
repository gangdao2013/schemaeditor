from enum import Enum

class EditMode(Enum):
    select=0 # 选择
    derive=1 # 创建派生关系
    ass=2 #连接关系

#单体对象：当前状态
class CurrState:
    __ins = None
    mode = EditMode.select

    @classmethod
    def init(cls):
        if cls.__ins == None:
            cls.__ins = cls()
        return cls.__ins

    def __init__(self):
        self.mode = EditMode.select