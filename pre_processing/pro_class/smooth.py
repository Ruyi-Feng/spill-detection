class Smoother:
    '''class Smoother

    平滑轨迹数据。
    '''
    def __init__(self, fps: int, smoothAlpha: int):
        '''function __init__

        input
        -----
        fps: int, 帧率
        smoothAlpha: int, 平滑系数
        '''
        self.fps = fps
        self.maxCompleteMs = smoothAlpha

    def run(self, records: dict, cars: dict) -> dict:
        '''function run

        input
        -----
        records: dict, 轨迹记录
        cars: dict, 车辆目标数据

        return
        ------
        records: dict, 轨迹记录, 平滑后

        平滑轨迹数据。
        '''
        return cars
