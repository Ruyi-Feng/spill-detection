import yaml
from road_calibration.algorithms import dbi, calQuartiles, poly2fit, poly2fitFrozen
import numpy as np


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

    def __init__(self, clbPath: str, laneWidth: float = 3.75,
                 emgcWidth: float = 3.5):
        '''class function __init__

        input
        ----------
        clbPath: str
            标定结果保存路径。
        laneWidth: float
            车道宽度。
        emgcWidth: float
            应急车道宽度。

        生成标定器，用于标定检测区域的有效行驶片区和应急车道。
        '''
        # 初始化属性
        self.clbPath = clbPath                  # 标定结果保存路径
        self.laneWidth = laneWidth              # 车道宽度
        self.emgcWidth = emgcWidth              # 应急车道宽度
        # 暂存传感器数据
        self.xyByLane = dict()                      # 按lane存储xy
        self.vxyCount = {'x': 0, 'y': 0}        # 存储所有vxy的正负计数
        # 暂存标定结果
        # 基础正方向与车道ID
        self.vDir = dict()
        self.laneIDs = []
        self.emgcIDs = []
        # 车道线方程
        self.xyMinMax = dict()                # 按lane存储xy的最大最小值
        self.totalXYMinMax = []           # 存储所有lane的xy最大最小值
        # 车道暂存属性
        self.laneProps = dict()                # 暂存lane的计算属性与结果
        # cell切割线方程
        self.SliceLines = []

    def recieve(self, msg):
        '''class function recieve

        input
        ----------
        msg: list
            list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。

        接受每帧传输来的目标信息, 更新给calibrator
        '''
        for target in msg:
            # if target['TargetId'] == 7390:
            #     # {'TargetId': 5087, 'XDecx': 2.57, 'YDecy': 7, 'ZDecz': 0,
            #     # 'VDecVx': 0.13, 'VDecVy': -19.3, 'Xsize': 0.47,
            #     # 'TargetType': 1, 'Longitude': 118.87387669811856,
            #     #  'Latitude': 31.935760760137626,
            #     # 'Confidence': 1, 'EventType': 0, 'LineNum': 1}
            #     # 只保留id和xy与vxvy, 删除其他
            #     keysToDelete = ['ZDecz', 'Xsize', 'Ysize',
            #                     'TargetType', 'Longitude', 'Latitude',
            #                     'Confidence', 'EventType']
            #     for k in keysToDelete:
            #         del target[k]
            #     print(target, ',', sep='')

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
        dir = self.__calibVDir()
        self.vDir = dir
        # 确定车道ID
        ids, emgc = self.__calibLaneIDs()
        self.laneIDs = ids
        self.emgcIDs = emgc
        self.laneProps = {id: dict() for id in ids}
        # 计算各lane的xy最大最小值
        xyMinMax, totalXYMinMax = self.__calibXYMinMax()
        self.xyMinMax = xyMinMax
        self.totalXYMinMax = totalXYMinMax
        # 标定内外侧车道线ID
        intID, extID = self.__calibIELanes()
        self.intID = intID
        self.extID = extID
        # 计算车道线方程
        lanesCoeff = self.__calibLanes()
        print(lanesCoeff)


    def __calibVDir(self) -> dict:
        '''class function __calibVDir

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

    def __calibLaneIDs(self) -> (list, list):
        '''class function __calibLanes

        return
        ----------
        ids: list
            返回车道ID号, list格式
        emgc: list
            返回应急车道号, list格式

        返回车道ID号, list格式。返回应急车道号, list格式。
        根据self.xyByLane统计车道ID号, 存为list。
        考虑到应急车道, 常规情况下交通量可能为0, 没有对应记录:
        若车道ID号不包含1号车道, 则将1号车道加入。
        上述操作完成后, 将车道ID设为从1到记录的max。
        若最大车道号为奇数, 则补充车道号加1。
        应急车道为1号车道和最大号车道。
        '''
        ids = list(self.xyByLane.keys())
        m = max(ids)
        if m % 2 == 1:    # 若最大车道号为奇数, 则补充车道号加1
            m += 1
        ids = list(range(1, m+1))
        emgc = [1, m]
        return ids, emgc

    def __calibXYMinMax(self):
        '''class function __calibXYMinMax

        对各lane的xyByLane分别以x或y排序, 得到最大最小值, 存储到self.xyMinMax。
        self.xyMinMax索引为laneID, 值为[xmin, xmax, ymin, ymax]。
        并对所有lane得到的xyMinMax再次排序, 得到最大最小值, 存储到self.totalXYMinMax。
        self.totalXYMinMax值为[xmin, xmax, ymin, ymax]。
        '''
        xyMinMax = dict()
        totalXYMinMax = [0, 0, 0, 0]
        # 对各lane的xyByLane分别以x或y排序, 得到最大最小值, 存储到self.xyMinMax
        for lane in self.xyByLane:
            # 以x排序
            self.xyByLane[lane].sort(key=lambda x: x[0])
            xmin, xmax = self.xyByLane[lane][0][0], self.xyByLane[lane][-1][0]
            # 以y排序
            self.xyByLane[lane].sort(key=lambda x: x[1])
            ymin, ymax = self.xyByLane[lane][0][1], self.xyByLane[lane][-1][1]
            # 存储
            xyMinMax[lane] = [xmin, xmax, ymin, ymax]
            totalXYMinMax[0] = min(totalXYMinMax[0], xmin)
            totalXYMinMax[1] = max(totalXYMinMax[1], xmax)
            totalXYMinMax[2] = min(totalXYMinMax[2], ymin)
            totalXYMinMax[3] = max(totalXYMinMax[3], ymax)
        return xyMinMax, totalXYMinMax

    def __calibIELanes(self):
        '''class function __calibIELanes

        return
        ----------
        intID: int
            返回内侧车道ID号
        extID: int
            返回外侧车道ID号
        
        计算除应急车道的2个边界车道的轨迹点的分散程度, 
        从而确定内侧车道ID号与外侧车道ID号。
        一般来说, 内侧车道距离较短, 车辆轨迹点范围分布较集中, 
        外侧车道距离较长, 车辆轨迹点范围分布较分散。
        '''
        # 考量紧急车道内侧的2个车道, 点分散程度大的的车道为外侧车道
        lane2, laneN_1 = self.emgcIDs[0] + 1, self.emgcIDs[1] - 1
        dbi2, dbiN_1 = dbi(self.xyByLane[lane2]), dbi(self.xyByLane[laneN_1])
        if dbi2 < dbiN_1:
            intID, extID = lane2, laneN_1
        else:
            intID, extID = laneN_1, lane2
        return intID, extID

    def __calibLanes(self):
        '''class function __calibLanes

        return
        ----------

        利用存储的轨迹点信息, 计算车道特征点, 拟合出车道方程
        '''
        # 计算非应急车道的特征点
        for id in self.laneIDs:
            if id in self.emgcIDs:
                continue
            featPoints = calQuartiles(self.xyByLane[id])
            self.laneProps[id].update({'fp': featPoints})
        
        # 拟合laneExt车道线方程
        lanesCoeff = dict()
        extCoeff = poly2fit(np.array(self.laneProps[self.extID]['fp']))
        lanesCoeff[self.extID] = extCoeff

        # 拟合其他非应急车道的车道线方程
        for id in self.laneIDs:
            if (id in self.emgcIDs) | (id == self.extID):
                continue
            # 以extCoeff为初始值拟合
            a = poly2fitFrozen(np.array(self.laneProps[id]['fp']), extCoeff[0])
            lanesCoeff[id] = a
        
        # 拟合应急车道的车道线方程
        intCoeff = lanesCoeff[self.intID]
        d = (self.laneWidth + self.emgcWidth) / 2   # 边界车道-应急车道距离
        # 计算ext车道线方程系数的导数
        diffCoeff = np.polyder(np.poly1d(extCoeff))
        # 计算在x=0处的导数值（切线的k值）
        k = np.polyval(diffCoeff, 0)
        # 计算边界车道-应急车道距离在y轴上的投影距离
        dY = d * np.sqrt(1 + k**2)
        # 计算应急车道的车道线方程系数
        if lanesCoeff[self.extID][2] > lanesCoeff[self.intID][2]:
            aExtEmgc = [extCoeff[0], extCoeff[1], extCoeff[2] + dY]
            aIntEmgc = [intCoeff[0], intCoeff[1], intCoeff[2] - dY]
        else:
            aExtEmgc = [extCoeff[0], extCoeff[1], extCoeff[2] - dY]
            aIntEmgc = [intCoeff[0], intCoeff[1], intCoeff[2] + dY]
        # 存储应急车道的车道线方程系数
        if self.intID == self.emgcIDs[0] + 1:
            lanesCoeff[self.emgcIDs[0]] = np.array(aIntEmgc)
            lanesCoeff[self.emgcIDs[1]] = np.array(aExtEmgc)
        else:
            lanesCoeff[self.emgcIDs[0]] = np.array(aExtEmgc)
            lanesCoeff[self.emgcIDs[1]] = np.array(aIntEmgc)

        return lanesCoeff


    def save(self):
        '''class function save

        将标定结果保存到self.clbPath。
        '''
        traffic = dict()
        traffic['Q'] = 0
        traffic['vDir'] = self.vDir
        traffic['lnMng'] = dict()

        for id in range(self.emgcIDs[0], self.emgcIDs[1] + 1):

            traffic['lnMng'][id] = {
                'id': id,
                'len': 0,   # 待写入
                'emgc': False,  # 待写入
                'q': 0,
                'k': 0,
                'v': 0,
                'cells': self.__emptyCells(range(self.emgcIDs[0],
                                                 self.emgcIDs[1]+1),
                                           [True]*len(self.laneIDs)),   # 待写入
                'coeff': []     # 待写入
            }

        with open(self.clbPath, 'w') as f:
            yaml.dump(traffic, f)

        return traffic

    def __emptyCells(self, orders: list, valid: list) -> dict:
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
        cells = dict()
        for i in range(len(orders)):
            cells[orders[i]] = (self.__emptyCell(orders[i], valid[i]))
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
    calibrator.emgcIDs = [1, 8]
    calibrator.laneIDs = [1, 2, 3, 4, 5, 6, 7, 8]

    # 标定器标定
    calibrator.calibrate()

    # 标定器保存, 测试保存成功
    calibrator.save()
