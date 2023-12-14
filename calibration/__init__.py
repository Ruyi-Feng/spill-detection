import json


class Calibrator():
    '''class Calibrator

    properties
    ----------
    xyByLane: dict
        按lane存储xy。
    vxyCount: dict
        存储所有vxy的正负计数, 每一次x/y对应的正速度+1, 负速度-1。
    calibration: dict
        存储标定结果。包括: 应急车道号, 车道线方程, 元胞划分直线方程, 合流元胞编号。

    methods
    -------
    recieve(msg)
        接受每帧传输来的目标信息, 更新给calibrator
    calibrate()
        根据存储的数据计算标定结果。
    save(path)
        将标定结果保存到path。

    生成标定器，用于标定检测区域的有效行驶片区和应急车道。
    '''

    def __init__(self, clbPath: str):
        self.xyByLane = {}                      # 按lane存储xy
        self.vxyCount = {'x': 0, 'y': 0}        # 存储所有vxy的正负计数
        self.calibration = {}                   # 存储标定结果

    def recieve(self, msg):
        '''class function recieve

        input
        ----------
        msg: list
            list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。

        接受每帧传输来的目标信息, 更新给calibrator
        '''

    def calibrate(self):
        '''class function calibrate

        根据calibrator的属性计算标定结果。
        '''
        self.calibration = {}

    def save(self):
        '''class function save

        将标定结果保存到self.clbPath。
        '''
        with open(self.clbPath, 'w') as f:
            json.dump(self.calibration, f)
