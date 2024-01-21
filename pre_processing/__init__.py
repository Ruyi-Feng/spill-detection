from pre_processing.pro_class.smooth import Smoother
from pre_processing.pro_class.complete import Completer
from utils.car_utils import carsList2Dict, carsDict2List


class TargetManager():
    def __init__(self, comMaxFrm: int, smthA: float) -> None:
        self.tgtInLastFrm = dict()      # 存储活跃状态的各ID车辆target, 按ID索引
        self.tgtInCurFrm = dict()       # 存储当前帧各ID车辆target, 按ID索引
        self.IDInLastFrm = []           # 存储上一帧车辆目标的ID
        self.IDInCurFrm = []            # 存储当前帧车辆目标的ID
        self.lostIDs = []               # 存储当前帧丢失的ID
        self.newIDs = []                # 存储当前帧新出现的ID
        self.cmp = Completer(comMaxFrm)          # 补全器
        self.smth = Smoother(smthA)          # 平滑器

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
        curFrame = carsList2Dict(curFrame)
        # TODO 计算新增属性
        # TODO 形成历史数据存储
        self._update(curFrame)
        # TODO 接入cerebum的补全平滑
        curFrame, cmpltIDs = self._run_complt(curFrame)
        curFrame = self._run_smooth(curFrame)
        self._update_last()
        curFrame = carsDict2List(curFrame)
        return curFrame

    def _update(self, curFrame):
        '''
        接受每帧传输来的目标信息, 更新targetList
        '''
        # 更新target

    def _run_complt(self, curFrame):
        '''
        '''
        curFrame = self.cmp.run(curFrame)
        return curFrame

    def _run_smooth(self, curFrame):
        '''
        '''
        curFrame = self.smth.run(curFrame, curFrame)
        return curFrame

    def _update_last(self):
        '''
        更新上一帧的目标信息
        '''
        self.tgtInLastFrm = self.tgtInCurFrm
        self.IDInLastFrm = self.IDInCurFrm
