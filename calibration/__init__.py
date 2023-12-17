import yaml


class Calibrator():
    '''class Calibrator

    properties
    ----------
    xyByLane: dict
        按lane存储xy。
    vxyCount: dict
        存储所有vxy的正负计数, 每一次x/y对应的正速度+1, 负速度-1。
    calibration: dict
        存储标定结果。包括: 应急车道号, 车道线方程, 元胞划分直线方程, 合流元胞编号。

    methods
    -------
    recieve(msg)
        接受每帧传输来的目标信息, 更新给calibrator
    calibrate()
        根据存储的数据计算标定结果。
    save(path)
        将标定结果保存到path。

    生成标定器，用于标定检测区域的有效行驶片区和应急车道。
    '''

    def __init__(self, clbPath: str):
        self.clbPath = clbPath                  # 标定结果保存路径
        self.xyByLane = dict()                      # 按lane存储xy
        self.vxyCount = {'x': 0, 'y': 0}        # 存储所有vxy的正负计数
        # 暂存标定结果
        self.xyMinMax = dict()                # 按lane存储xy的最大最小值
        self.totalXYMinMax = []           # 存储所有lane的xy最大最小值
        self.LaneIDs = []
        self.emgcLanes = []
        self.SliceLines = []

    def recieve(self, msg):
        '''class function recieve

        input
        ----------
        msg: list
            list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。

        接受每帧传输来的目标信息, 更新给calibrator
        '''
        print(msg[0])
        for target in msg:
            if target['LineNum'] >= 100:
                continue    # 换道过程中的车辆，非标准车道编号的不计入标定

            # 更新xyByLane
            if target['LineNum'] not in self.xyByLane:
                self.xyByLane[target['LineNum']] = []

            self.xyByLane[target['LineNum']].append(
                [target['XDecx'], target['YDecy']])

            # 更新vxyCount
            if target['VDecVx'] > 0:
                self.vxyCount['x'] += 1
            elif target['VDecVx'] < 0:
                self.vxyCount['x'] -= 1
            if target['VDecVy'] > 0:
                self.vxyCount['y'] += 1
            elif target['VDecVy'] < 0:
                self.vxyCount['y'] -= 1

    def calibrate(self):
        '''class function calibrate

        根据calibrator的属性计算标定结果。
        '''
        self.calibration = dict()
        # 确定运动正方向
        dir = self.__calibDir()
        self.calibration['dir'] = dir
        # 计算各lane的xy最大最小值
        self.__calibXYMinMax()  # 赋值属性self.xyMinMax, self.totalXYMinMax

    def __calibDir(self) -> dict:
        '''class function __calibDir

        return
        ----------
        返回运动正方向, dict格式, {'x': 1, 'y': 1}。
        '''
        dir = {'x': 1, 'y': 1}
        if self.vxyCount['x'] < 0:
            dir['x'] = -1
        if self.vxyCount['y'] < 0:
            dir['y'] = -1
        return dir

    def __calibXYMinMax(self):
        '''class function __calibXYMinMax

        对各lane的xyByLane分别以x或y排序, 得到最大最小值, 存储到self.xyMinMax。
        self.xyMinMax索引为laneID, 值为[xmin, xmax, ymin, ymax]。
        并对所有lane得到的xyMinMax再次排序, 得到最大最小值, 存储到self.totalXYMinMax。
        self.totalXYMinMax值为[xmin, xmax, ymin, ymax]。
        '''
        # 对各lane的xyByLane分别以x或y排序, 得到最大最小值, 存储到self.xyMinMax
        for lane in self.xyByLane:
            # 以y排序
            self.xyByLane[lane].sort(key=lambda x: x[1])
            ymin, ymax = self.xyByLane[lane][0][1], self.xyByLane[lane][-1][1]
            # 以x排序
            self.xyByLane[lane].sort(key=lambda x: x[0])
            xmin, xmax = self.xyByLane[lane][0][0], self.xyByLane[lane][-1][0]
            # 存储
            self.xyMinMax[lane] = [xmin, xmax, ymin, ymax]
            self.totalXYMinMax[0] = min(self.totalXYMinMax[0], xmin)
            self.totalXYMinMax[1] = max(self.totalXYMinMax[1], xmax)
            self.totalXYMinMax[2] = min(self.totalXYMinMax[2], ymin)
            self.totalXYMinMax[3] = max(self.totalXYMinMax[3], ymax)

    def save(self):
        '''class function save

        将标定结果保存到self.clbPath。
        '''
        traffic = dict()
        traffic['Q'] = 0
        traffic['lnMng'] = dict()

        for id in range(self.emgcLanes[0], self.emgcLanes[1] + 1):

            traffic['lnMng'][id] = {
                'id': id,
                'len': 0,   # 待写入
                'emgc': False,  # 待写入
                'q': 0,
                'k': 0,
                'v': 0,
                'cells': self.__emptyCells(range(self.emgcLanes[0],
                                                 self.emgcLanes[1]+1),
                                           [True]*len(self.LaneIDs)),   # 待写入
                'coeff': {
                    'left': [],   # 待写入
                    'right': [],  # 待写入
                    'mid': []      # 待写入
                }
            }

        with open(self.clbPath, 'w') as f:
            yaml.dump(traffic, f)

    def __emptyCells(self, orders: list, valid: list) -> list:
        '''class function __emptyCells

        input
        ----------
        orders: list
            元胞编号。
        valid: list
            元胞是否有效。

        return
        ----------
        返回一个空元胞列表。
        '''
        cells = []
        for i in range(len(orders)):
            cells.append(self.__emptyCell(orders[i], valid[i]))
        return cells

    def __emptyCell(self, order: int = 0, valid: bool = True) -> dict:
        '''class function __emptyCell

        input
        ----------
        order: int
            元胞编号。

        return
        ----------
        返回一个空元胞。
        '''
        return {
            'order': order,
            'valid': valid,
            'q': 0,
            'k': 0,
            'v': 0,
            'vCache': [],
            'danger': 0.0
        }


if __name__ == '__main__':
    # 生成标定器
    clbPath = './calibration/clb.yml'
    calibrator = Calibrator(clbPath)
    calibrator.emgcLanes = [1, 8]
    calibrator.LaneIDs = [1, 2, 3, 4, 5, 6, 7, 8]

    # 标定器标定
    calibrator.calibrate()

    # 标定器保存, 测试保存成功
    calibrator.save()
