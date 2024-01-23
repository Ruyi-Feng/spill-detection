import json


class Smltor():
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

    def run(self):
        '''
        每运行一次run()函数, 读取一行数据, 返回该行数据。
        并再下次运行时读取下一行数据。
        函数会返回list类型的数据, 或者str类型的消息。
        '''
        msg = self.f.readline()
        # 接受数据
        try:
            msg = json.loads(msg)  # 接收到list数据
        except Exception:
            pass    # 非检测信息则会接收到str数据
        return msg


if __name__ == "__main__":
    from pathlib import Path
    p = (Path(__file__) / './../../data/heartbeat.txt').resolve()
    s = Smltor(str(p))

    while True:
        a = s.run()
        if a == '':
            break
        print(a)
