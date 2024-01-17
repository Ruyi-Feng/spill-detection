from traffic_manager.lane_manager import LaneMng
from typing import Dict     # 引入以方便调用类方法


class TrafficMng():
    '''class TrafficManager

    交通流计算类，根据传感器信息计算交通流。
    唯一对外接口函数: `update(cars)`, 返回值为None。
    实现tm对车辆进行按帧缓存, 并每隔一定时间计算交通流参数。

    Attributes
    ----------
    fps: float
        frequency per second, 传感器采样频率
    qd: float
        QDuration, 用于计算小时交通流量的流量采样时长, 单位: 帧(cfg中为s)
    itv: float
        interval, 更新计算交通参数的间隔时间, 单位: 帧(cfg中为s)
    Q: float
        存储整个路段的交通流量(单位: 辆/h)
    count: int
        接收计数。计算时若持续时间小于qd, 则通过count进行比例计算。
        note: count不能一直累加, 达到某一足够大的数值后应当进行清理。
              或者让count达到检测时间后自动清零。代码中采用第二种方法。
        如果能拿到时间戳，利用时间戳计算会方便一些。
    lanes: dict
        车道管理器, 按照车道管理车道属性和交通流参数
    cacheRet: int
        cache retention, 缓存保存时长, 单位: 帧

    '''
    def __init__(self, clb: dict, cfg: dict):
        '''function __init__
        input
        -----
        clb: dict
            raod calibration, 标定的车道配置信息
        cfg: dict
            算法配置参数
        '''
        # 参数
        self.fps = cfg['fps']
        self.qd = cfg['traffic']['q_duration'] * self.fps        # 单位帧
        self.itv = cfg['traffic']['cal_interval'] * self.fps     # 单位帧
        self.cacheRet = max(self.qd, self.itv)  # 缓存保存时长(/frame)
        self.cellLen = cfg['calib']['cell_len']   # 元胞长度
        # 状态属性
        self.Q = 0          # 存储整个路段的交通流量(单位: 辆/h)
        self.count = 0      # 接收计数, 仅用于判定某一帧是否应当计算交通流参数, 达到itv后重置为0
        self.lanes = self._initLanes(clb, cfg)  # 按照车道管理车道属性和交通流参数

    def _initLanes(self, clb: dict, cfg: dict) -> Dict[int, LaneMng]:
        '''function _initLanes

        input
        -----
        clb: dict
            raod calibration, 标定的车道配置信息, 格式如下
        cfg: dict
            算法配置参数

        return
        ------
        lanes: dict
            车道管理器, 按照车道管理车道属性和交通流参数,
            键为车道id, 值为LaneMng车道管理器实例

        生成车道管理器, 按照车道管理车道属性和交通流参数。
        '''
        lanes = {}
        for laneID in clb:
            lc = clb[laneID]    # lane calibration
            lm = LaneMng(laneID, lc['emgc'],
                         lc['len'], lc['start'], lc['end'],
                         lc['vDir']['y'], lc['coef'],
                         self.cellLen, lc['cells'],
                         cfg, self.cacheRet)
            lanes[laneID] = lm
        return lanes

    def update(self, cars):
        '''function update

        input
        -----
        cars: list, 传感器数据, cars元素为代表一个车辆目标的dict。

        接收传感器数据, 更新缓存, 一定时间更新交通流参数。
        该方法不直接返回数据, 各层次的交通数据通过直接调用实例本身获取。
        '''
        self.count += 1
        self.count %= self.itv  # 重置计数, count仅用于判断计算交通流的时机, 达到后即可置零

        # 更新缓存数据
        self._updateCache(cars)
        if self.count % self.itv == 0:
            self._updateTraffic()
            print(self.Q, end=', ')

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
        # 输出检查
        # print('t=', self.count, end='\t')
        # for id in self.lanes:
        #     print('lane',id, '=', int(self.lanes[id].q), end=' ')
        # print('Q=', int(self.Q))

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
        carsByLane = {id: [] for id in self.lanes}
        for car in cars:
            laneID = car['LineNum'] - 100 if car['LineNum'] > 100 \
                else car['LineNum']     # 大于100的减去100
            carsByLane[laneID].append(car)
        return carsByLane
