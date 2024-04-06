from .utils import carsList2Dict, carsDict2List
from .pro_class.calculate import VandAccCalculator
from .pro_class.complete import Completer
from .pro_class.smooth import Smoother

ACCELERATION_CALCULATE_FRAMES = 5         # 计算加速度帧数
NO_UPDATE_DATA_MAX_CACHE_MS = 10000     # ms, 无更新数据最大缓存时间
TRAJECTORY_MAX_CACHE_MS= 30000           # ms, 轨迹最大缓存时间


class PreProcessor:
    '''class PreProcessor

    预处理器, 用于对数据进行预处理, 暂存处理属性并提升数据质量。

    具体功能
    -------
    1. 过滤目标初始检测数据。以删除幽灵误检目标
    2. 过滤不在首尾区域的目标数据。以删除中间区域出现的误检目标。
    3. 过滤全程速度过低的目标数据。重点观注当前帧速度较低的目标, 以排除误检目标。
    4. 补全拼接断裂的轨迹数据。以提升数据质量。
    properties
    ----
    cfg: dict, 配置文件
    clb: dict, 标定参数

    parameters
    ----------
    filterLowSpeed: float, m/s, 速度过滤阈值
    filterEdgeLength: float, m, 边缘过滤长度
    completeMs: int, ms, 补全时间
    smoothAlpha: float, 平滑系数
    filterInitMs: int, ms, 初始过滤时间

    '''
    def __init__(self, cfg: dict, clb: dict):
        '''function __init__
        
        input
        -----
        cfg: dict, 配置文件
        clb: dict, 标定参数
        '''
        self.cfg = cfg
        self.clb = clb
        # 车道首尾范围
        self.laneEdge = self._calculateTragetAppearEdge()
        # 轨迹记录
        self.latestTimestamp = -1
        self.records = dict()
        # 子处理器
        self.vaCal = VandAccCalculator(ACCELERATION_CALCULATE_FRAMES)
        self.completer = Completer(cfg['fps'], cfg['completeMs'])
        self.smoother = Smoother(cfg['fps'], cfg['smoothAlpha'])

    def run(self, cars: list) -> list:
        '''function run

        input
        -----
        cars: list, 数据

        return
        ------
        cars: list, 处理后的数据

        预处理数据, 返回处理后的数据。
        '''
        # 更新最新时间戳
        self._updateLatestTimestamp(cars)
        # 将cars转化为dict
        cars = carsList2Dict(cars)
        # 预处理
        # print('before prepro', len(cars), end='    ')
        # 1. 过滤不在首尾区域的目标数据
        cars = {id: car for id, car in cars.items()
                if self._inLaneEdge(car) or (id in self.records)}
        # print('after filter edge', len(cars), end='    ')
        # 2. 更新records
        self._updateRecords(cars)
        # 3. 计算全局速度和加速度
        cars = self.vaCal.run(self.records, cars)
        # print('after vaCal', len(cars), end='    ')
        # 4. 补全拼接断裂的轨迹数据
        cars = self.completer.run(self.records, cars)
        # print('after completer', len(cars), end='    ')
        # 5. 当前帧数据平滑
        cars = self.smoother.run(self.records, cars)
        # print('after smoother', len(cars), end='    ')
        # 6. 从records中获取当前帧数据
        cars = {id: self.records[id][-1] for id in cars.keys()}
        # print('after get last', len(cars), end='    ')
        # 7. 过滤全程速度过低的目标数据
        cars = {id: car for id, car in cars.items()
                if car['globalSpeed'] > self.cfg['filterLowSpeed']}
        # print('after filter low speed', len(cars), end='    ')
        # 8. 过滤初始产生的目标数据
        # if len(cars) == 0:
        #     return cars
        # print(self.latestTimestamp, cars[list(cars.keys())[0]]['timestamp'])
        cars = {id: car for id, car in cars.items()
                if self.latestTimestamp - self.records[id][0]['timestamp'] >
                self.cfg['filterInitMs']}
        # print('after filter init', len(cars), end='    ')
        # print('-----------------')
        # 将cars转化为list
        cars = carsDict2List(cars)
        return cars

    def _updateLatestTimestamp(self, cars: dict):
        '''function _updateLatestTimestamp

        input
        -----
        cars: dict, 车辆目标数据

        更新最新时间戳, 并保存为自身属性。
        '''
        self.latestTimestamp = max(self.latestTimestamp, cars[0]['timestamp'])

    def _updateRecords(self, cars: dict):
        '''function _updateRecords

        input
        -----
        cars: dict, 数据

        return
        ------
        None, 将当前接受的cars数据更新到records

        更新车辆缓存数据records
        '''
        # 补充车辆轨迹
        for id, car in cars.items():
            if id not in self.records:
                self.records[id] = [car]
            else:
                self.records[id].append(car)
        # 删除无用轨迹
        for id in list(self.records.keys()):
            # 删除过久车辆轨迹
            deltaMs1 = self.latestTimestamp - \
                self.records[id][-1]['timestamp']
            if deltaMs1 > NO_UPDATE_DATA_MAX_CACHE_MS:
                del self.records[id]
                continue
            # 删除过长车辆轨迹
            deltaMs2 = self.records[id][-1]['timestamp'] - \
                self.records[id][0]['timestamp']
            if deltaMs2 > TRAJECTORY_MAX_CACHE_MS:
                self.records[id].pop(0)
        return

    def _calculateTragetAppearEdge(self):
        '''function _calculateTragetAppearEdge

        return
        ------
        dict, 车辆目标出现的首尾范围

        计算车辆目标出现的首尾范围, 按车道组织, 存为自身属性
        考虑标定的cell的valid情况,
        若车道首或尾有相连的不可用cell,
        则需要考虑这些cell的长度.
        '''
        laneEdge = dict()
        for laneID, lane in self.clb.items():
            cells = lane['cells']
            # 获取车道有效的行驶范围
            if lane['vDir']['y'] == 1:
                yLow = lane['start']
                yHigh = lane['end']
                i = 0
                while (0 <= i < len(cells)) and (not cells[i]):
                    yLow += self.cfg['cellLen']
                    i += 1
                i = len(cells) - 1
                while (0 <= i < len(cells)) and (not cells[i]):
                    yHigh -= self.cfg['cellLen']
                    i -= 1
            elif lane['vDir']['y'] == -1:   # cell存储按驾驶正方向
                yLow = lane['end']
                yHigh = lane['start']
                i = 0
                while (0 <= i < len(cells)) and (not cells[i]):
                    yHigh -= self.cfg['cellLen']
                    i += 1
                i = len(cells) - 1
                while (0 <= i < len(cells)) and (not cells[i]):
                    yLow += self.cfg['cellLen']
                    i -= 1
            # 获取首尾边界的限定范围
            yLow += self.cfg['filterEdgeLength']
            yHigh -= self.cfg['filterEdgeLength']
            laneEdge[laneID] = (yLow, yHigh)
        self.laneEdge = laneEdge
        return laneEdge

    def _inLaneEdge(self, car: dict) -> bool:
        '''function _inLaneEdge

        input
        -----
        car: dict, 车辆目标数据

        return
        ------
        bool, 是否在车道首尾范围内出现

        判断车辆是否在车道首尾范围内出现
        '''
        yLow, yHigh = self.laneEdge[car['laneID']]
        # 判断车辆是否在车道首尾范围内
        inMiddlePart = yLow < car['y'] < yHigh
        return not inMiddlePart
