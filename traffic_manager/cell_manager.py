class CellMng:
    '''class Cell
    实例化道路元胞
    '''
    def __init__(self, laneID: int, order: int, valid: bool):
        self.laneID = laneID
        self.order = order
        self.valid = valid
        self.vCache = []
        self.q = 0
        self.k = 0
        self.v = 0
        self.danger = 0.0
    
    def update(self, vCache: list):
        '''function update
        更新元胞属性
        '''
        self.vCache = vCache
        self.q = len(vCache)
        self.k = len(vCache) / self.len
        self.v = sum(vCache) / len(vCache)
        self.danger = self.k * self.v