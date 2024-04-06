

class Completer:
    '''class Completer

    补全拼接断裂的轨迹数据。
    '''
    def __init__(self, fps: int, maxCompleteMs: int):
        '''function __init__

        input
        -----
        fps: int, 帧率
        maxCompleteMs: int, ms, 最大补全时间
        '''
        self.fps = fps
        self.maxCompleteMs = maxCompleteMs

    def run(self, records: dict, cars: dict) -> dict:
        '''function run

        input
        -----
        records: dict, 轨迹记录
        cars: dict, 车辆目标数据

        return
        ------
        records: dict, 轨迹记录, 补全后

        补全拼接断裂的轨迹数据。
        '''
        return cars
