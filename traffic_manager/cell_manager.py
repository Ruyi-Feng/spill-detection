class CellMng:
    '''class Cell
    实例化道路元胞

    Attributes
    ----------
    laneID : int
        元胞所在车道ID
    order : int
        元胞在车道中的序号
    valid : bool
        元胞是否有效
    len : float
        元胞长度
    start : float
        元胞起始位置
    end : float
        元胞结束位置
    q : float
        元胞流量, 单位: veh/h
    k : float
        元胞密度, 单位: veh/km
    v : float
        元胞速度, 单位: m/s(计算q时, 注意调整单位为km/h)
    r1s : float
        rate1 standard, 元胞默认随时间减小的置信度标准值
    r1 : float
        rate1, 元胞默认随时间增长的置信度, 按r1s * q / qs更新
    r2 : float
        rate2, 过大横向速度和换道导致的前向元胞置信度增加值
    danger : float
        元胞存在抛洒物的危险性
    cache : list
        元胞缓存车辆实例, 按接收顺序索引
        TODO: 直接缓存车辆整个信息会不会炸内存? 还是只缓存必要信息?
    cacheRet: int
        cache retention, 缓存最长时间, 超出此时间的缓存被清除, 单位: 帧
    '''
    def __init__(self, laneID: int, order: int, valid: bool,
                 len: float, start: float, end: float,
                 tt: float, fps: float, qs: float, r2: float,
                 cacheRet: float):
        '''function __init__

        input
        -----
        laneID : int
            元胞所在车道ID
        order : int
            元胞在车道中的序号
        valid : bool
            元胞是否有效
        len : float
            元胞长度
        start : float
            元胞起始位置
        end : float
            元胞结束位置
        tt : float
            t tolerance, 用于影响元胞置信度时间增长率r1的时间容忍度, 单位: s
        fps : float
            frequency per second, 传感器采样频率
        qs : float
            q standard, 用于影响元胞置信度时间增长率r1的标准流量, 单位: veh/h
        r2 : float
            rate2, 过大横向速度和换道导致的前向元胞置信度增加值
        cacheRet: int
            cache retention, 缓存最长时间, 超出此时间的缓存被清除, 单位: 帧
        '''
        # 基础属性
        self.laneID = laneID
        self.order = order
        self.valid = valid
        self.len = len
        self.start = start
        self.end = end
        # 交通参数
        self.q = 0
        self.k = 0
        self.v = 0
        self.aveCarNum = 0  # 帧平均车辆数
        # 置信度
        self.r1s = 1 / tt / fps
        self.qs = qs
        self.r1 = 0
        self.r2 = r2
        self.danger = 0.0
        # 缓存
        self.cache = []    # list内按顺序索引, 用dict反而会有遍历的消耗
        self.cacheRet = cacheRet

    def updateCache(self, cars: list):
        '''function update

        input
        -----
        cars: list
            车辆列表, 每个元素为一个dict, 代表一个车辆目标

        1. 更新元胞缓存, 将已确定归属于该元胞的车辆目标, 更新到cache中。
        2. 要更新danger。
        若当前帧没有车辆处于该cell, 则以空占位,
        保证在没有时间戳索引的情况下, 能够用list自身的索引代替时间戳,
        空数据能够占位代表过去了1个时间戳。
        '''
        # 缓存
        self.cache.append(cars)
        # 检查缓存长度, 清除过期缓存
        if len(self.cache) > self.cacheRet:
            self.cache.pop(0)
        # 更新danger
        self._updateDanger()

    def updateTraffic(self):
        # 确定缓存数据量
        baseT = len(self.cache) if len(self.cache) < self.cacheRet \
            else self.cacheRet
        # 合并各帧目标数据
        cars = [car for frame in self.cache for car in frame]
        aveCarNum = len(cars) / baseT
        self.aveCarNum = aveCarNum
        # 计算k(单位: veh/km)
        self.k = aveCarNum / self.len * 1000
        # 计算v(单位: m/s)
        self.v = 0 if aveCarNum == 0 else \
            abs(sum([car['VDecVy'] for car in cars])) / len(cars)
        # 计算q(单位: veh/h)
        self.q = self.k * self.v * 3.6
        # TODO 每次更新交通参数, 更新rate1数值

    def _updateDanger(self):
        '''function _updateDanger

        更新元胞存在抛洒物的危险性
        '''
        # TODO 计算danger
        pass
