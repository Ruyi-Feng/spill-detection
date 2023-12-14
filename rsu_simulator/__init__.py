class Smltor():
    '''class Smltor

    仿真器，用于仿真传感器数据的传输。每运行一次，读取一行数据，返回该行数据，并再下次运行时读取下一行数据。
    初始化：记录仿真数据文件路径。

    '''
    def __init__(self, dataPath: str):
        '''function __init__

        input
        -----
        dataPath: str
            仿真数据文件路径
        '''
        self.dataPath = dataPath

    def run(self):
        '''利用seek函数，每运行一次run()函数，读取一行数据，返回该行数据。并再下次运行时读取下一行数据。
        '''
