'''Define class Connector to recieve radar stream bytes,
   and transfer hex data into structured data.'''


class Converter:
    '''class Converter

    将radar传输来的信息, 其中的目标信息(2004), 转化为结构化数据

    报文类型包括:
    1 心跳报文 2002 TCP 8089 1s 雷达主送
    2 跟踪信息集报文 2004 TCP 8089 50ms 雷达主送
    3 实时统计信息 2031 TCP 8089 雷达发送
    4 周期统计信息 2032 TCP 8089 雷达发送
    5 拥堵信息上报 2074 TCP 8089 雷达发送

    properties
    ----------
    msgType : int, 报文类型

    '''
    def __init__(self):
        '''function __init__
        
        定义目标信息转化的基本配置
        '''
        self.head0 = 0xA5           # 报文头特征码0
        self.head1 = 0x5A           # 报文头特征码1
        self.msgLenOffset = 2       # 报文长度偏移量
        self.msgLenByteLen = 2      # 报文长度字节数
        self.msgTypeOffset = 4      # 报文类型偏移量
        self.msgTypeByteLen = 2     # 报文类型字节数
        self.msgType = 2004         # 2004跟踪信息集报文
        self.timeOffset = 6         # 时间偏移量
        self.timeByteLen = 8        # 时间字节数
        self.frameOffset = 14       # 帧号偏移量
        self.frameByteLen = 2       # 帧号字节数
        self.numOffset = 16         # 目标数偏移量
        self.numByteLen = 2         # 目标数字节数
        self.objectLen = 37         # 目标信息长度
        self.endMarkLen = 1         # 结束标志长度
        self.validationLen = 2      # 校验长度

    def convert(self, bytes: bytes) -> list:
        '''function convert

        input
        -----
        bytes : bytes, 16进制数据消息

        return
        ------
        msg: list, 结构化数据信息
        将16进制数据消息, 转化为多个目标结构化数据组成的list
        '''

        pass


class Connector(Converter):
    '''class Connector

    根据主地址, 获取到雷达数据流地址, 获取雷达流数据,
    将雷达流数据从16进制转化为结构化数据, 并POST发送。
    '''
    def __init__(self):
        super().__init__()
