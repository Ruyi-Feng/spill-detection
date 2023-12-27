import yaml
import numpy as np
from road_calibration.algorithms import (
    dbi, calQuartiles, poly2fit, poly2fitFrozen, cutPts)


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

    def __init__(self, clbPath: str, fps: float,
                 laneWidth: float = 3.75, emgcWidth: float = 3.5,
                 cellLen: float = 50.0, qMerge: float = 0):
        '''class function __init__

        input
        ----------
        clbPath: str
            标定结果保存路径。
        fps: float
            帧率。
        laneWidth: float
            车道宽度。
        emgcWidth: float
            应急车道宽度。
        cellLen: float
            元胞长度。
        qMerge: float
            判定元胞为合流区域的流量, 小于qMerge判定该cell不可用。

        生成标定器，用于标定检测区域的有效行驶片区和应急车道。
        '''
        # 初始化属性
        self.clbPath = clbPath                  # 标定结果保存路径
        self.fps = fps                          # 帧率
        self.laneWidth = laneWidth              # 车道宽度
        self.emgcWidth = emgcWidth              # 应急车道宽度
        self.cellLen = cellLen                  # 元胞长度
        self.qMerge = qMerge                    # 判定元胞为合流区域的流量
        self.count = 0                          # 计数
        # 暂存传感器数据
        self.xyByLane = dict()                  # lane索引的xy
        self.vxyCount = dict()                  # lane索引的vxy的正负计数
        # 车道ID与运动正方向
        self.laneIDs = []
        self.emgcIDs = []
        self.vDir = dict()
        # 车道线方程
        self.xyMinMax = dict()                  # lane索引的xy的最大最小值
        self.globalXYMinMax = []    # 全局xy最大最小值[xmin,max, ymin,max]
        self.polyPts = dict()                     # lane索引的四分位特征点
        self.coef = dict()                        # lane索引的曲线方程系数
        # 元胞
        self.cells = dict()                       # lane索引的元胞有效无效列表

    def recieve(self, msg):
        '''class function recieve

        input
        ----------
        msg: list
            list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。

        接受每帧传输来的目标信息, 更新给calibrator
        '''
        self.count += 1
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

            laneID = target['LineNum'] - 100 if target['LineNum'] > 100 \
                else target['LineNum']

            # 分配dict索引()
            if laneID not in self.xyByLane:
                self.xyByLane[laneID] = []
                self.vxyCount[laneID] = {'x': 0, 'y': 0}
            # 存储vxy
            self.xyByLane[laneID].append([target['XDecx'], target['YDecy']])
            # 更新vxyCount
            if target['VDecVx'] > 0:
                self.vxyCount[laneID]['x'] += 1
            elif target['VDecVx'] < 0:
                self.vxyCount[laneID]['x'] -= 1
            if target['VDecVy'] > 0:
                self.vxyCount[laneID]['y'] += 1
            elif target['VDecVy'] < 0:
                self.vxyCount[laneID]['y'] -= 1

    def calibrate(self):
        '''class function calibrate

        根据calibrator的属性计算标定结果。
        '''
        # 确定车道ID
        self.laneIDs, self.emgcIDs = self._calibLaneIDs()
        # 标定内外侧车道线ID
        self.intID, self.extID = self._calibIELaneID()
        # 确定运动正方向
        self.vDir = self._calibVDir()
        # 计算各lane的xy最大最小值
        self.xyMinMax, self.globalXYMinMax = self._calibXYMinMax()
        # 计算各lane轨迹四分位特征点
        self.polyPts = self._calibPolyPts()
        # 计算车道线方程
        self.coef = self._calibLanes()
        # 划分元胞
        self.cells = self._calibCells()

    def _calibLaneIDs(self) -> (list, list):
        '''class function _calibLanes

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

    def _calibIELaneID(self):
        '''class function _calibIELaneID

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

    def _calibVDir(self) -> dict:
        '''class function _calibVDir

        return
        ----------
        返回运动正方向, dict格式, {'x': 1, 'y': 1}。
        '''
        dirDict = dict()
        # 确定非应急车道速度正方向
        for id in self.laneIDs:
            if id in self.emgcIDs:
                continue    # 跳过应急车道, 轨迹点数量少不具有代表性
            dir = {'x': 1, 'y': 1}
            if self.vxyCount[id]['x'] < 0:
                dir['x'] = -1
            if self.vxyCount[id]['y'] < 0:
                dir['y'] = -1
            dirDict[id] = dir
        # 确定应急车道速度正方向
        for id in self.emgcIDs:
            if id == 1:
                dirDict[id] = dirDict[id+1]  # 1号车道与2号车道同向
            else:
                dirDict[id] = dirDict[id-1]  # 最大车道与倒数第二车道同向    
        return dirDict

    def _calibXYMinMax(self):
        '''class function _calibXYMinMax

        对各lane的xyByLane分别以x或y排序, 得到最大最小值, 存储到self.xyMinMax。
        self.xyMinMax索引为laneID, 值为[xmin, xmax, ymin, ymax]。
        并对所有lane得到的xyMinMax再次排序, 得到最大最小值, 存储到self.globalXYMinMax。
        self.globalXYMinMax值为[xmin, xmax, ymin, ymax]。
        '''
        xyMinMax = dict()
        globalXYMinMax = [0, 0, 0, 0]
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
            globalXYMinMax[0] = min(globalXYMinMax[0], xmin)
            globalXYMinMax[1] = max(globalXYMinMax[1], xmax)
            globalXYMinMax[2] = min(globalXYMinMax[2], ymin)
            globalXYMinMax[3] = max(globalXYMinMax[3], ymax)
        return xyMinMax, globalXYMinMax

    def _calibPolyPts(self) -> dict:
        '''class function _calibPolyPts

        return
        ----------
        polyPts: dict
            返回车道特征点, dict格式, {laneID: [list]}。
            元素为一个lane轨迹点的四分位特征点, shape=(5, 2)。
        '''
        polyPts = dict()
        for id in self.laneIDs:
            if id in self.emgcIDs:
                continue
            featPoints = calQuartiles(self.xyByLane[id])
            polyPts.update({id: featPoints})
        return polyPts

    def _calibLanes(self):
        '''class function _calibLanes

        return
        ----------

        利用存储的轨迹点信息, 计算车道特征点, 拟合出车道方程
        '''
        # 拟合laneExt车道线方程
        lanesCoef = dict()
        # 实验验证: 采用四分位特征点拟合效果优于直接用轨迹点拟合
        extCoef = poly2fit(np.array(self.polyPts[self.extID]))
        # extCoef = poly2fit(np.array(self.xyByLane[self.extID]))
        lanesCoef[self.extID] = extCoef

        # 拟合其他非应急车道的车道线方程
        for id in self.laneIDs:
            if (id in self.emgcIDs) | (id == self.extID):
                continue
            # 以extCoef为初始值拟合
            # 实验验证: 采用四分位特征点拟合效果优于直接用轨迹点拟合
            a = poly2fitFrozen(np.array(self.polyPts[id]), extCoef[0])
            # a = poly2fitFrozen(np.array(self.xyByLane[id]), extCoef[0])
            lanesCoef[id] = a

        # 拟合应急车道的车道线方程
        intCoef = lanesCoef[self.intID]
        d = (self.laneWidth + self.emgcWidth) / 2   # 边界车道-应急车道距离
        # 计算ext车道线方程系数的导数
        diffCoef = np.polyder(np.poly1d(extCoef))
        # 计算在x=0处的导数值（切线的k值）
        k = np.polyval(diffCoef, 0)
        # 计算边界车道-应急车道距离在y轴上的投影距离
        dY = d * np.sqrt(1 + k**2)
        # 计算应急车道的车道线方程系数
        if lanesCoef[self.extID][2] > lanesCoef[self.intID][2]:
            aExtEmgc = [extCoef[0], extCoef[1], extCoef[2] + dY]
            aIntEmgc = [intCoef[0], intCoef[1], intCoef[2] - dY]
        else:
            aExtEmgc = [extCoef[0], extCoef[1], extCoef[2] - dY]
            aIntEmgc = [intCoef[0], intCoef[1], intCoef[2] + dY]
        # 存储应急车道的车道线方程系数
        if self.intID == self.emgcIDs[0] + 1:
            lanesCoef[self.emgcIDs[0]] = np.array(aIntEmgc)
            lanesCoef[self.emgcIDs[1]] = np.array(aExtEmgc)
        else:
            lanesCoef[self.emgcIDs[0]] = np.array(aExtEmgc)
            lanesCoef[self.emgcIDs[1]] = np.array(aIntEmgc)

        return lanesCoef

    def _calibCells(self):
        '''class function _calibCells

        return
        ----------
        cells: dict
            返回元胞有效无效列表, dict格式, {laneID: [list]}。
            元素为一个lane的元胞有效无效列表,如[True, True, False]。
            对于双向道路, 标定出的cells有效否的顺序, 为沿着车道向前行驶的正方向。
        '''
        # 按全局y最大最小值与元胞长度划分元胞
        ymin, ymax = self.globalXYMinMax[2], self.globalXYMinMax[3]
        pts = cutPts(ymin, ymax, self.cellLen)   # 元胞划分点包括起点终点
        cellNum = len(pts) - 1                   # 元胞数量

        # 各lane将xy点分配到元胞顺序计数
        cellCount = dict()
        for id in self.laneIDs:
            count = [0] * cellNum
            for xy in self.xyByLane[id]:
                # 根据y大于等于划分点的数量, 确定元胞编号
                order = np.sum(xy[1] >= pts)
                count[order] += 1
            cellCount[id] = count

        cells = dict()
        for id in self.laneIDs:
            # 计算各元胞在一小时内的经过车辆数
            valid = []
            for i in range(cellNum):
                q = cellCount[id][i] / (self.count / self.fps) * 3600
                valid.append(True if q >= self.qMerge else False)
            # 对于y运动方向为负的车道, 元胞列表反向(默认从ymin到ymax划分为正向)
            if self.vDir[id]['y'] < 0:
                valid.reverse()
            cells[id] = valid
        return cells

    def save(self):
        '''class function save

        将标定结果保存到self.clbPath。
        '''
        traffic = dict()
        traffic['range'] = {'start': 0, 'len': 0, 'end': 0}
        traffic['lanes'] = dict()
        for id in self.laneIDs:
            laneClb = { 'emgc': False if id not in self.emgcIDs else True,
                       'vDir': self.vDir[id],
                       'coef': self.coef[id],
                       'cells': self.cells[id]
                       }
            traffic['lanes'].update({id: laneClb})

        with open(self.clbPath, 'w') as f:
            yaml.dump(traffic, f)

        return traffic


if __name__ == '__main__':
    # 生成标定器
    clbPath = './calibration/clb.yml'
    calibrator = Calibrator(clbPath, 20)
    calibrator.emgcIDs = [1, 8]
    calibrator.laneIDs = [1, 2, 3, 4, 5, 6, 7, 8]

    # 标定器标定
    calibrator.calibrate()

    # 标定器保存, 测试保存成功
    calibrator.save()
