from pre_processing.pro_class.smooth import Smoother
from pre_processing.pro_class.complete import Completer
from pre_processing.pro_class.id_correct import IDCorrector


class TargetManager():
    def __init__(self, comMaxFrm: int, smthA: float) -> None:
        self.tgtInLastFrm = dict()      # 存储活跃状态的各ID车辆target, 按ID索引
        self.tgtInCurFrm = dict()       # 存储当前帧各ID车辆target, 按ID索引
        self.IDInLastFrm = []           # 存储上一帧车辆目标的ID
        self.IDInCurFrm = []            # 存储当前帧车辆目标的ID
        self.lostIDs = []               # 存储当前帧丢失的ID
        self.newIDs = []                # 存储当前帧新出现的ID
        self.crt = IDCorrector()        # ID跳变修正器, 可能要设置到completer之下的一个属性TODO
        self.cmp = Completer(comMaxFrm)          # 补全器
        self.smth = Smoother(smthA)          # 平滑器

    def run(self, curTgt: list) -> list:
        '''function run

        input
        -----
        curTgt: list
            当前帧车辆目标信息

        return
        ------
        curTgt: list
            预处理后的当前帧车辆目标信息

        接收当前帧的传感器数据:
        1. 更新除tgtInLastFrm, IDInLastFrm以外的所有属性。
        2. 进行补全, 平滑运算。
        3. 更新tgtInLastFrm, IDInLastFrm。
        '''
        self._update(curTgt)
        curTgt, cmpltIDs = self._run_complt(curTgt)
        curTgt, _ = self.crt.run(curTgt, cmpltIDs)
        curTgt = self._run_smooth(curTgt)
        self._update_last()
        return curTgt

    def _update(self, curTgt):
        '''
        接受每帧传输来的目标信息, 更新targetList
        '''
        # 更新target

    def _run_IDCorrect(self, curTgt):
        '''function __run_IDCorrect

        input
        -----
        curTgt: list
            当前帧车辆目标信息

        return
        ------
        curTgt: list
            当前帧车辆目标信息

        '''
        self.crt.run()

    def _run_complt(self, curTgt):
        '''
        '''
        curTgt = self.cmp.run(curTgt)
        return curTgt

    def _run_smooth(self, curTgt):
        '''
        '''
        curTgt = self.smth.run(curTgt, curTgt)
        return curTgt

    def _update_last(self):
        '''
        更新上一帧的目标信息
        '''
        self.tgtInLastFrm = self.tgtInCurFrm
        self.IDInLastFrm = self.IDInCurFrm
