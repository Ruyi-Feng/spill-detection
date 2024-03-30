from pre_processing.pro_class.smooth import Exponential
from pre_processing.pro_class.complete import Interpolation
from utils.car_utils import carsList2Dict, carsDict2List
from pre_processing.utils import framesCombination, getCurrentFrame

from copy import deepcopy


class PreProcessor():
    def __init__(self, comMaxFrm: int, smthA: float) -> None:
        self.cmp = Interpolation(comMaxFrm * 1000)  # 补全器(输入ms)
        self.smth = Exponential(smthA)              # 平滑器
        self.contextFrames = dict()                 # 按id索引的历史数据
        self.lastTimestamp = None                   # 上一帧时间戳

    def run(self, curFrame: list) -> list:
        '''function run

        input
        -----
        curFrame: list, 当前帧车辆目标信息

        return
        ------
        curFrame: list, 预处理后的当前帧车辆目标信息

        接收当前帧的传感器数据:
        1. 更新除tgtInLastFrm, IDInLastFrm以外的所有属性。
        2. 进行补全, 平滑运算。
        3. 更新tgtInLastFrm, IDInLastFrm。
        note
        -----
        算法会原地实时修改历史数据。
        '''
        # 初次启动
        if (self.lastTimestamp is None) & (len(curFrame) != 0):
            self.lastTimestamp = curFrame[0]['timestamp']
        # 处理0值speed数据
        # curFrame = self._fixSpeed0(curFrame)
        # 给车辆timestamp属性做个备份
        curFrame = self._copyTimestamp(curFrame)
        # dict组织方便索引
        curFrame = carsList2Dict(curFrame)
        # 如果不开补全平滑
        # _, self.lastTimestamp = framesCombination(self.contextFrames,
        #                                                 curFrame,
        #                                                 self.lastTimestamp)
        # curFrame = getCurrentFrame(self.contextFrames, self.lastTimestamp)

        # 补全
        curFrame, self.lastTimestamp = self.cmp.run(self.contextFrames,
                                                    curFrame,
                                                    self.lastTimestamp)
        # 平滑
        curFrame, self.lastTimestamp = self.smth.run(self.contextFrames,
                                                     curFrame,
                                                     self.lastTimestamp)
        # 计算a属性
        curFrame = self._calAcceleration(self.contextFrames, curFrame)
        # 返回为list形式车辆
        curFrame = carsDict2List(curFrame)
        # 用time覆盖timestamp
        curFrame = self._recoverTimestamp(curFrame)
        return curFrame

    def _calAcceleration(self, contextFrames: dict, curFrame: dict) -> dict:
        '''function _calAcceleration

        input
        -----
        contextFrames: dict, 历史帧数据
        curFrame: dict, 当前帧数据

        return
        ------
        curFrame: dict, 计算加速度后的当前帧数据

        根据历史数据contextFrame与当前帧数据curFrame, 利用数据已有的vx与vy计算加速度a
        '''
        newCurFrame = dict()
        for key in curFrame.keys():
            newCurFrame[key] = curFrame[key]
            newCurFrame[key]['ax'] = 0
            newCurFrame[key]['ay'] = 0
            newCurFrame[key]['a'] = 0
            if key in contextFrames.keys():
                if len(contextFrames[key]) > 1:
                    # 这里已经对context做了当前帧补充，因此上一帧的索引为-2
                    deltaVx = curFrame[key]['vx'] - \
                        contextFrames[key][-2]['vx']
                    deltaVy = curFrame[key]['vy'] - \
                        contextFrames[key][-2]['vy']
                    deltaT = (curFrame[key]['timestamp'] -
                              contextFrames[key][-2]['timestamp']) / 1000
                    newCurFrame[key]['ax'] = deltaVx / deltaT
                    newCurFrame[key]['ay'] = deltaVy / deltaT
                    newCurFrame[key]['a'] = (newCurFrame[key]['ax']**2 +
                                             newCurFrame[key]['ay']**2)**0.5
        return newCurFrame

    def _fixSpeed0(self, curFrame: list) -> list:
        '''function _fixSpeed0

        input
        -----
        curFrame: list, 当前帧车辆目标信息

        return
        ------
        curFrame: list, 修正后的当前帧车辆目标信息

        修正速度为0的数据, 部分车辆速度值为0, 但vx和vy有数值
        '''
        for car in curFrame:
            if (car['speed'] == 0) & ((car['vx'] > 1) or (car['vy'] > 1)):
                car['speed'] = (car['vx']**2 + car['vy']**2)**0.5

        return curFrame

    def _copyTimestamp(self, cars: list):
        '''
        将车辆的timestamp属性备份出time
        '''
        newCars = []
        for car in cars:
            car['time'] = deepcopy(car['timestamp'])
            newCars.append(car)

        return newCars

    def _recoverTimestamp(self, cars: list):
        '''
        把存储有car原始unix毫秒单位的时间戳time, 覆盖到timestamp
        '''
        newCars = []
        for car in cars:
            car['timestamp'] = deepcopy(car['time'])
            newCars.append(car)
        return newCars
