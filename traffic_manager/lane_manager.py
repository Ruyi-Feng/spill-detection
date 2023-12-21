from traffic_manager.cell_manager import CellMng


class LaneMng:
    '''class Lane
    按照车道管理车道属性和交通流参数
    '''
    def __init__(self, id: int, emg: bool,
                 len: float, start: float, end: float, vdir: int,
                 coef: dict,
                 cellLen: float, clbCell: dict):
        ''' function __init__
        input
        -----
        id: int
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
        clbCell: dict
            元胞标定参数
        '''
        # 基础属性
        self.id = id
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
        self.cells = self._initCells(clbCell)

    def _initCells(self, clbCell: dict) -> dict:
        '''function _initCells
        初始化车道元胞
        '''
        pass

    def updateCache(self, cars: list):
        '''function updateCache
        更新车道元胞缓存
        '''
        # 确定车辆所在元胞, 按元胞组织车辆
        carsByCell = self._carsLocCell(cars)
        # 按元胞更新缓存
        for order in self.cells:
            self.cells[order].updateCache(carsByCell[order])

    def updateTraffic(self):
        '''function updateTraffic
        更新车道交通流参数
        '''
        # 按元胞更新交通流参数
        for order in self.cells:
            self.cells[order].updateTraffic()

    def _carsLocCell(self, cars: list) -> dict:
        '''function _carsLocCell

        input
        -----
        cars: list
            车辆列表, 每个元素为一个dict, 代表一个车辆目标

        return
        ------
        carsLocCell: dict
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
        order = self.vdir * (car['YDecy'] - self.start) // self.cellLen
        return order
