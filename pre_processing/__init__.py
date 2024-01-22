from pre_processing.pro_class.smooth import Exponential
from pre_processing.pro_class.complete import Interpolation
from utils.car_utils import carsList2Dict, carsDict2List


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
        '''
        # 初次启动
        if (self.lastTimestamp == None) & (len(curFrame) != 0):
            self.lastTimestamp = curFrame[0]['timeStamp']
        # dict组织方便索引
        curFrame = carsList2Dict(curFrame)
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
        # TODO 更新history？看补全平滑是否已经实现补充数据
        # 返回为list形式车辆
        curFrame = carsDict2List(curFrame)
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
            newCurFrame[key]['a'] = 0
            if key in contextFrames.keys():
                if len(contextFrames[key]) > 1:
                    # TODO 看这里是否已经对context做了补充，补充了则索引-2，未补充则索引-1
                    newCurFrame[key]['a'] = \
                        (curFrame[key]['vx'] - contextFrames[key][-2]['vx']) / \
                        (curFrame[key]['timeStamp'] - contextFrames[key][-2]['timeStamp'])
        return newCurFrame
