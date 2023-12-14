class Completer():
    '''class Completer

    用于补全缺失轨迹数据.
    需要记录下需要进行补全的ID, 以及补全的帧数, 判断是否继续补全.
    '''
    def __init__(self, maxFrm: int):
        '''function __init__

        input
        -----
        maxFrm: int
            最大补全帧数

        '''
        self.maxFrm = maxFrm

    def run(self, curTgt: list) -> (list, list):
        '''function run

        input
        -----
        curTgt: list
            当前帧车辆目标信息

        return
        ------
        curTgt: list
            计算后的当前帧车辆目标信息
        cmpltIDs: list
            需要补全的ID

        '''
        cmpltIDs = self.__get_cmpltIDs(curTgt)
        curTgt = self.__cmplt(curTgt, cmpltIDs)
        return curTgt, cmpltIDs
