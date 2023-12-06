
def preProcess(msg):
    '''
    将传来的数据预处理为算法需要的格式
    input
    ------
    msg: list, 传感器数据

    output
    ------
    msg: list, 传感器数据
    targets: list[dict], 存储单个目标的轨迹信息
    '''
