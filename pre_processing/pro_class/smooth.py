class Smoother():
    '''class Smoother

    利用上一帧平滑轨迹计算当前帧的轨迹平滑结果。
    原理: 三次指数平滑。
    三次指数平滑公式
    -----

    '''
    def __init__(self, alpha: float):
        '''function __init__

        input
        -----
        alpha: int
            三次指数平滑的平滑指数。0 < alpha < 1

        '''
        self.alpha = alpha

    def run(self, curTgt: list, lastTgt: list) -> list:
        '''function run

        input
        -----
        curTgt: list
            当前帧车辆目标信息
        lastTgt: list
            上一帧车辆目标信息

        return
        ------
        curTgt: list
            计算后的当前帧车辆目标信息

        '''
        resultTgt = []
        for tgt in curTgt:
            resultTgt.append(tgt)

        return resultTgt

    def __smooth(self, tgt: dict, lastTgt: dict) -> dict:
        '''function __smooth

        input
        -----
        tgt: dict
            当前帧车辆目标信息
        lastTgt: list
            上一帧车辆目标信息

        return
        ------
        tgt: dict
            计算后的当前帧车辆目标信息

        '''

        # tgt['x'] = exp3Smooth(tgt['x'], self.alpha,
        #                           lastTgt['smth']['x'])
        # tgt['y'] = exp3Smooth(tgt['y'], self.alpha,
        #                           lastTgt['smth']['y'])
        return tgt


def exp3Smooth(now: float, alpha: float, last: list) -> float:
    '''function exp3Smooth

    input
    -----
    now: float
        当前时刻数据
    alpha: float
        平滑指数
    last: list
        上一时刻的1次平滑, 2次平滑, 3次平滑数值

    return
    ------
    result: float
        三次指数平滑结果

    利用三次指数平滑方法，输入当前接收的未平滑数据, 平滑指数α,
    以及上一时刻接收的1, 2, 3平滑值, 返回当前时刻的平滑预测值。
    '''
    result = 0
    return result
