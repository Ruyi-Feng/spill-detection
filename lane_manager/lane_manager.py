class Cell:
    '''class Cell
    实例化道路元胞
    '''
    def __init__(self, laneid: int, ) -> None:
        pass


class Lane:
    '''class Lane
    按照车道管理车道属性和交通流参数
    '''
    def __init__(self, id: int, emg: bool, len: float, coeff: dict,
                 cell: dict):
        ''' function __init__

        定义属性：
        1. 车道编号
        2. 是否为应急车道
        3. 车道长度
        4. 车道线方程（左右中）
        5. 可以再定义一个子class表示cell, 按order索引cell,
        cell包含: lane, order, vCache, q, k, v, danger
        '''
        self.id = id
        self.emg = emg
        self.len = len
        self.coeff = coeff
        self.cell = cell
