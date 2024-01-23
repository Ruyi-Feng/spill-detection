from traffic_manager.cell_manager import CellMng
from typing import Dict


class LaneMng:
    '''class Lane
    按照车道管理车道属性和交通流参数
    对外接口函数: `updateCache(cars)`, `updateTraffic(), updateDanger()`, 返回值为None。
    用于被上层trafficMng调用, 每帧将调用更新缓存, 每个指定时间更新traffic。
    该2个函数的调用顺序不可颠倒, 内部实际为调用cell的2个更新函数。

    Attributes
    ----------
    ID: int
        车道ID
    emg: bool
        是否为应急车道
    len: float
        车道长度
    start: float
        车道起始位置
    end: float
        车道结束位置
    vdir: int
        车道沿y轴的正方向, 1为正向, -1为反向
    coef: dict
        车道标定参数
    cellLen: float
        元胞长度
    cellsValid: list
        元胞是否可用列表
    cfg: dict
        算法配置参数, 主要应用于cell生成
    cacheRet: int
        cache retention, 缓存保存时长, 单位: 帧
    cells: dict
        键为元胞序号order, 值为CellMng实例
    q: float
        车道交通流量, 单位: 辆/小时
    k: float
        车道密度, 单位: 辆/公里
    v: float
        车道平均速度, 单位: 公里/小时

    Methods
    -------
    _initCells(cfg: dict) -> Dict[int, CellMng]
        初始化车道元胞
    updateCache(cars: list)
        更新车道元胞缓存
    updateTraffic()
        更新车道交通流参数
    _carsByCell(cars: list) -> dict
        按照车道的start, end, cellLen,与车辆的YDecy属性,
        确定车辆所在元胞序号, 并按元胞组织车辆。
    _carLocCell(car: dict) -> int
        根据车道的start, end, cellLen,与车辆的YDecy属性,
        确定车辆所在元胞序号。

    '''
    def __init__(self, ID: int, emg: bool,
                 len: float, start: float, end: float,
                 vdir: int, coef: dict,
                 cellLen: float, cellsValid: list,
                 cfg: dict, cacheRet: int):
        ''' function __init__
        input
        -----
        ID: int
            车道ID
        emg: bool
            是否为应急车道
        len: float
            车道长度
        start: float
            车道起始位置
        end: float
            车道结束位置
        vdir: int
            车道沿y轴的正方向, 1为正向, -1为反向
        coef: dict
            车道标定参数
        cellLen: float
            元胞长度
        cellsValid: list
            元胞是否可用列表
        cfg: dict
            算法配置参数, 主要应用于cell生成
        cacheRet: int
            cache retention, 缓存保存时长, 单位: 帧
        '''
        # 基础属性
        self.ID = ID
        self.emg = emg
        self.len = len          # 暂无使用
        self.start = start
        self.end = end          # 暂无使用
        self.vdir = vdir
        self.coef = coef
        # 交通参数
        self.q = 0
        self.k = 0
        self.v = 0
        # 元胞属性
        self.cellLen = cellLen
        self.cellsValid = cellsValid
        self.cacheRet = cacheRet
        self.cells = self._initCells(cfg)

    def _initCells(self, cfg: dict) -> Dict[int, CellMng]:
        '''function _initCells

        input
        -----
        cfg: dict
            算法配置参数

        return
        ------
        cells: dict
            键为元胞序号order, 值为CellMng实例

        初始化车道元胞
        '''
        cells = {}
        start = self.start
        if self.vdir == -1:    # 若为反向, 则start设置为超出yamx范围的cellLen整数倍
            start = (self.start // self.cellLen + 1) * self.cellLen
        end = start + self.cellLen * self.vdir
        for i in range(len(self.cellsValid)):
            cells[i] = CellMng(self.ID, i, self.cellsValid[i],
                               self.cellLen, start, end,
                               cfg['tTolerance'],
                               cfg['fps'],
                               cfg['qStandard'],
                               cfg['rate2'],
                               cfg['vLateral'],
                               self.cacheRet)
            # print([self.ID, i, self.cellsValid[i],
            #                    self.cellLen, start, end])
            start = end
            end = start + self.cellLen * self.vdir
        return cells

    def updateCache(self, cars: list):
        '''function updateCache

        input
        -----
        cars: list
            车辆列表, 每个元素为一个dict, 代表一个车辆目标
        t: int
            接收到该数据的帧号, 作为键值索引缓存数据

        更新车道元胞缓存
        '''
        # 确定车辆所在元胞, 按元胞组织车辆
        carsByCell = self._carsByCell(cars)
        # 按元胞更新缓存
        for order in self.cells:
            self.cells[order].updateCache(carsByCell[order])

    def updateTraffic(self):
        '''function updateTraffic
        更新车道交通流参数
        '''
        # 更新元胞交通流参数
        for order in self.cells:
            self.cells[order].updateTraffic()
        # 更新车道交通流参数
        aveCarNum = 0   # 按帧的平均车辆数
        vSum = 0   # 车道平均速度
        for order in self.cells:
            aveCarNum += self.cells[order].aveCarNum
            vSum += self.cells[order].v * self.cells[order].aveCarNum
        self.k = aveCarNum / self.len * 1000
        self.v = vSum / aveCarNum if aveCarNum != 0 else 0  # 加权求速度
        self.q = self.k * self.v * 3.6

    def updateR1(self, q: float):
        '''function updateR1

        input
        -----
        q: float
            整个路段交通流量, 单位: 辆/小时

        将路段q数据传递给各个cell, 用于更新cell抛洒物置信度随时间增长的rate1
        '''
        for order in self.cells:
            self.cells[order].updateR1(q)

    def updateDanger(self):
        '''function updateDanger

        更新cell的危险系数
        '''
        for order in self.cells:
            # 按时间增加r1, 并检查是否需要让前方cell增加r2
            PossibleFrontSpill, _ = self.cells[order].updateDanger()
            # 如果当前遍历的cell发现可能有抛洒物, 前方cell更新危险度+r2
            if PossibleFrontSpill:
                for frontOrder in self.cells:
                    if frontOrder <= order:
                        continue
                    self.cells[frontOrder].updateDangerPassive()

    def resetCellDetermineStatus(self):
        '''function resetCellDetermineStatus

        重置cell的determine状态
        '''
        for order in self.cells:
            self.cells[order].resetCellDetermineStatus()

    def _carsByCell(self, cars: list) -> dict:
        '''function _carsByCell

        input
        -----
        cars: list
            车辆列表, 每个元素为一个dict, 代表一个车辆目标

        return
        ------
        carsByCell: dict
            键为元胞序号order, 值为所分配车辆的列表, 无车辆则为空列表

        按照车道的start, end, cellLen,与车辆的YDecy属性,
        确定车辆所在元胞序号, 并按元胞组织车辆。
        '''
        # 按cell的order为键值预生成字典
        carsByCell = {i: [] for i in range(len(self.cells))}
        # 遍历车辆确定元胞
        for car in cars:
            order = self._carLocCell(car)
            carsByCell[order].append(car)
        return carsByCell

    def _carLocCell(self, car: dict) -> int:
        '''function _carLocCell

        input
        -----
        car: dict
            车辆目标

        return
        ------
        order: int
            车辆所在元胞序号

        根据车道的start, end, cellLen,与车辆的YDecy属性,
        确定车辆所在元胞序号。
        '''
        order = self.vdir * (car['y'] - self.start) // self.cellLen
        return order
