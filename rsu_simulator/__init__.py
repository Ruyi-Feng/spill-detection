import json
import pandas as pd
from utils import swapQuotes
from utils.file_read import BigFileReader


class Smltor(BigFileReader):
    '''class Smltor

    仿真器, 用于仿真传感器数据的传输。每运行一次, 读取一行数据, 返回该行数据, 并再下次运行时读取下一行数据。
    初始化: 记录仿真数据文件路径。

    '''
    def __init__(self, dataPath: str):
        '''function __init__

        input
        -----
        dataPath: str
            仿真数据文件路径
        '''
        self.dataPath = dataPath
        self.f = open(self.dataPath, 'r')
        # super().__init__(dataPath)
        # self.runIndex = -1

    def run(self):
        '''
        每运行一次run()函数, 读取一行数据, 返回该行数据。
        并再下次运行时读取下一行数据。
        函数会返回list类型的数据, 或者str类型的消息。
        '''
        msg = self.f.readline()
        # self.runIndex += 1
        # msg = self.getRow(self.runIndex)
        # msg = swapQuotes(msg)
        # 接受数据
        try:
            msg = json.loads(msg)  # 接收到list数据
        except Exception:
            pass    # 非检测信息则会接收到str数据
        return msg


class DfSimulator:
    '''class DfSimulator

    仿真器, 用于仿真传感器数据的传输。每运行一次, 读取一行数据, 返回该行数据, 并再下次运行时读取下一行数据。
    区别在于, 该仿真器直接从csv文件读取数据。
    仅适用于小型测试场景, 因采用pandas包, 故不适用于大型数据集。
    '''

    def __init__(self, dataPath: str):
        '''function __init__

        input
        -----
        dataPath: str
            仿真数据文件路径
        '''
        self.dataPath = dataPath
        self.df = pd.read_csv(dataPath)
        self.runIndex = -1

    def run(self):
        '''
        每运行一次run()函数, 读取一行数据, 返回该行数据。
        并再下次运行时读取下一行数据。
        对于df数据, 需要根据每行数据和列名生成dict数据。
        '''
        self.runIndex += 1
        if self.runIndex >= len(self.df):
            return ''
        row = self.df.iloc[self.runIndex]
        msg = {}
        for k in row.keys():
            msg[k] = row[k]
        return [msg]    # 返回列表, 模拟每帧有多条数据, 统一格式

class DumpSimulator:
    '''class DumpSimulator

    仿真器, 用于仿真传感器数据的传输。每运行一次, 读取一行数据, 返回该行数据, 并再下次运行时读取下一行数据。
    区别在于, 该仿真器直接从16进制文件读取16进制数据。
    '''


if __name__ == "__main__":
    from pathlib import Path
    p = (Path(__file__) / './../../data/heartbeat.txt').resolve()
    s = Smltor(str(p))

    while True:
        a = s.run()
        if a == '':
            break
        print(a)
