import math

class VandAccCalculator:
    '''class VandACalculator
    
    计算速度、全局速度和加速度属性,
    speed, globalSpeed,
    ax, ay, a.
    '''
    def __init__(self, accCalculateFrames: int):
        '''function __init__
        
        加速度计算帧数, 在一定范围内采样计算加速度。'''
        self.accCalculateFrames = accCalculateFrames
        pass

    def run(self, records: dict, cars: dict) -> dict:
        '''function run

        input
        -----
        records: dict, 轨迹记录
        cars: dict, 车辆目标数据

        return
        ------
        cars: dict, 车辆目标数据, 增加了全局速度和加速度属性

        计算全局速度和加速度。
        '''
        for id, car in cars.items():
            car['speed'] = math.sqrt(car['vx']**2 + car['vy']**2)
            # 计算全局速度m/s
            if len(records[id]) < 2:
                car['globalSpeed'] = math.sqrt(car['vx']**2 + car['vy']**2)
            else:
                car['globalSpeed'] = 1000 * math.sqrt(
                    (records[id][-1]['x'] - records[id][0]['x'])**2 +
                    (records[id][-1]['y'] - records[id][0]['y'])**2
                    ) / (records[id][-1]['timestamp'] -
                        records[id][0]['timestamp'])
            # 计算加速度m/s^2
            if len(records[id]) < self.accCalculateFrames:
                car['ax'], car['ay'], car['a'] = 0, 0, 0
            else:
                car['ax'] = 1000 * (
                    records[id][-1]['vx'] -
                    records[id][-self.accCalculateFrames]['vx']) / (
                        records[id][-1]['timestamp'] -
                        records[id][-self.accCalculateFrames]['timestamp'])
                car['ay'] = 1000 * (
                    records[id][-1]['vy'] -
                    records[id][-self.accCalculateFrames]['vy']) / (
                        records[id][-1]['timestamp'] -
                        records[id][-self.accCalculateFrames]['timestamp'])
                car['a'] = math.sqrt(car['ax']**2 + car['ay']**2)
        return cars
