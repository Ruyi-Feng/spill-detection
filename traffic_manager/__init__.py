from traffic_manager.lane_manager import LaneMng
from typing import Dict


class TrafficMng():
    '''class TrafficManager

    交通流计算类，根据传感器信息计算交通流

    Attributes
    ----------
    fps: float
        frequency per second, 传感器采样频率
    qd: float
        QDuration, 用于计算小时交通流量的流量采样时长, 单位: 帧(config中为s)
    itv: float
        interval, 更新计算交通参数的间隔时间, 单位: 帧(config中为s)
    Q: float
        存储整个路段的交通流量(单位: 辆/h)
    count: int
        接收计数。计算时若持续时间小于qd, 则通过count进行比例计算。
        TODO count不能一直累加, 达到某一足够大的数值后应当进行清理？
        如果能拿到时间戳，利用时间戳计算会方便一些。
    lanes: dict
        车道管理器, 按照车道管理车道属性和交通流参数

    '''
    def __init__(self, fps: float, qd: float, itv: float, clb: dict):
        '''function __init__
        input
        -----
        qd: float
            QDuration, 用于计算小时交通流量的流量采样时长
        itv: float
            interval, 更新计算交通参数的间隔时间
        fps: float
            frequency per second, 传感器采样频率
        clb: dict
            raod calibration, 标定的车道配置信息
        '''
        # 参数
        self.fps = fps           # 传感器采样频率
        self.qd = qd * fps       # 用于计算小时交通流量的流量采样时长
        self.itv = itv * fps     # 更新计算交通参数的间隔时间
        self.clearItv = max(self.qd, self.itv)  # 清理周期, 保障数据清理前的计算
        # 状态属性
        self.Q = 0          # 存储整个路段的交通流量(单位: 辆/h)
        self.count = 0      # 接收计数，计算时若未达到qd等其他计算需求，手动进行比例计算
        self.lanes = self._initLanes(clb)  # 车道管理器, 按照车道管理车道属性和交通流参数

    def _initLanes(self, clb: dict) -> Dict[int, LaneMng]:
        '''function _initLanes

        input
        -----
        clb: dict
            raod calibration, 标定的车道配置信息

        output
        ------
        lanes: dict
            车道管理器, 按照车道管理车道属性和交通流参数
        '''

        pass

    def update(self, cars):
        '''function update

        input
        -----
        cars: list, 传感器数据, cars元素为代表一个车辆目标的dict。

        接收传感器数据, 更新缓存, 一定时间更新交通流参数。
        '''
        self.count += 1
        # 更新缓存数据
        self._updateCache(cars)
        if self.count % self.itv == 0:
            self._updateTraffic()

    def _updateCache(self, cars: list):
        '''function _updateCache

        input
        -----
        cars: list, 传感器数据, cars元素为代表一个车辆目标的dict。

        仅更新缓存数据, 增加新数据, 删除过期数据。
        '''
        # 按车道组织车辆
        carsByLane = self._carsByLane(cars)  # dict按车道组织, 无车则空列表
        # 更新至各车道缓存
        for id in self.lanes:
            self.lanes[id].updateCache(carsByLane[id])

    def _updateTraffic(self):
        '''function _updateTraffic

        根据已更新的实例缓存的交通数据属性, 更新计算交通流参数。
        '''
        # 更新交通流参数
        for id in self.lanes:
            self.lanes[id].updateTraffic()
        # 更新整个路段的交通流量
        self._updateQ()

    def _updateQ(self):
        '''function _updateQ

        更新整个路段的交通流量
        '''
        # 计算路段交通流量
        self.Q = 0
        for id in self.lanes:
            self.Q += self.lanes[id].q

    def _carsByLane(self, cars: list) -> dict:
        '''function carsByLane

        input
        -----
        cars: list
            车辆列表, 每个元素为一个dict, 代表一个车辆目标

        return
        ------
        carsByLane: dict
            键为车道id, 值为所分配车辆的列表, 无车辆则为空列表

        确定车辆所在车道, 按车道组织车辆, 车道号大于100则减去100。
        '''
        carsByLane = {i.ID: [] for i in self.lanes}
        for car in cars:
            laneID = car['LineNum'] - 100 if car['LineNum'] > 100 \
                else car['LineNum']     # 大于100的减去100
            carsByLane[laneID].append(car)
        return carsByLane
