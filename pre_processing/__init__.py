from pre_processing.pro_class.smooth import Exponential
from pre_processing.pro_class.complete import Interpolation
from utils.car_utils import carsList2Dict, carsDict2List


class PreProcessor():
    def __init__(self, comMaxFrm: int, smthA: float) -> None:
        self.cmp = Interpolation(comMaxFrm)     # 补全器
        self.smth = Exponential(smthA)          # 平滑器
        self.history = dict()                   # 按id索引历史数据

    def run(self, curFrame: list) -> list:
        '''function run

        input
        -----
        curFrame: list
            当前帧车辆目标信息

        return
        ------
        curFrame: list
            预处理后的当前帧车辆目标信息

        接收当前帧的传感器数据:
        1. 更新除tgtInLastFrm, IDInLastFrm以外的所有属性。
        2. 进行补全, 平滑运算。
        3. 更新tgtInLastFrm, IDInLastFrm。
        '''
        # dict组织方便索引
        curFrame = carsList2Dict(curFrame)
        # TODO 接入cerebum的补全平滑
        # TODO 计算新增属性
        # 返回为list形式车辆
        curFrame = carsDict2List(curFrame)
        return curFrame
