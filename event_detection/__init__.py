import math
from logger import MyLogger
from traffic_manager import TrafficMng
from event_detection.event import EventMng
from utils import delDictKeys, strCapitalize, unixMilliseconds2Datetime
from utils.car_utils import getCarFromCars, getCarBaseInfo


'''The module is to detect events. Params are defined in config.yml.'''


class EventDetector(TrafficMng):
    '''class EventDetector

    事件检测类, 用于检测交通事件。继承TrafficMng类, 用于获取交通流信息。
    唯一对外调用函数: `run(cars)`, 用于更新交通流信息, 检测交通事件, 输出并返回事件列表。
    此种定义下, 在外围调用时, 无需生成TrafficMng类,
    只需生成EventDetector类即可, EventDetector可直接调用TrafficMng的方法。

    Properties
    ----------
    fps: float
        frequency per second, 传感器采样频率
    eventTypes: list
        eventTypes需要检测的事件列表, 包括: 抛撒物检测,
        停车检测, 低速行驶检测, 超速行驶检测, 急停车检测,
        事故检测, 拥堵检测, 非法占用应急车道检测。

    检测参数
    -------
    抛洒物检测类
    tTolerance: float, 事件持续时间容忍度, 单位s
    qStandard:  float, 标准情况的道路通行流量, 单位v/h
    vLateral:   float, 抛洒物横向运动置信度增长率
    rate2:      float, 抛洒物横向运动置信度增长率
    WarnFreq: int, 抛洒物报警频率, 单位帧
    异常行驶类
    vStop:        float, 准静止判定速度阈值, 单位m/s
    durationStop: float, 准静止持续时间阈值, 单位s
    vLow:           float, 低速阈值, 单位m/s
    durationLowSpeed:    float, 低速持续时间阈值, 单位s
    vHigh:          float, 高速阈值, 单位m/s
    durationHighSpeed:   float, 高速持续时间阈值, 单位s
    aEmgcBrake:       float, 急刹车加速度阈值(绝对值), 单位m/s^2
    durationEmgcBrake: float, 急刹车持续时间阈值, 单位s
    车辆碰撞检测类
    dTouch:     float, 车辆碰撞判定距离, 单位m
    tSupervise: float, 车辆碰撞监控时间, 单位s
    拥堵检测类
    densityCrowd: float, 拥堵密度阈值, 单位辆/km
    vCrowd:       float, 拥堵速度阈值, 单位m/s
    非法占道类
    durationIllegalOccupation: float, 非法占道持续时间阈值, 单位s

    TODO 非必要, 将各类别事件的dict, func都以字典形式存储, 更简洁且易于理解
    '''
    def __init__(self, clb: dict, cfg: dict,
                 logger: MyLogger = None):
        ''' function __init__

        input
        ------
        clb: dict, 已标定的参数字典
        cfg: dict, 配置参数字典
        event_types: list, 需要检测的事件列表
        logger: MyLogger, 日志记录器

        生成事件检测器, 用于检测交通事件。
        '''
        # 令TrafficMng方法初始化给自身
        super().__init__(clb, cfg)
        self.logger = logger if logger else MyLogger('Driver', 20)
        # 生成事件管理器
        self.eventMng = EventMng()
        # 初始化属性(其中秒为单位属性, 统一初次赋值后, 乘fps以帧为单位)
        self.clb = clb
        self.fps = cfg['fps']
        for param in cfg:
            self.__setattr__(param, cfg[param])

        # # 更新参数单位从秒到帧（因采用timestamp而弃用）
        # self._initTimePropertiesUnitTrans2Frames()

        # 初始化潜在事件记录变量
        self.currentIDs = []    # 当前帧车辆id列表
        self.potentialEventTypes = ['stop', 'lowSpeed', 'highSpeed',
                                    'emgcBrake', 'illegalOccupation']
        # 记录数据格式为: {车辆id: [开始时间, 当前时间, car, eventID]}, 当达到持续阈值或者事件结束时, 报警
        self.stopDict = dict()
        self.lowSpeedDict = dict()
        self.highSpeedDict = dict()
        self.emgcBrakeDict = dict()
        self.illegalOccupationDict = dict()
        # 以两辆车id为索引, 记录监测时间
        self.incidentDict = dict()
        # 以车道id+cell order为索引, 记录[开始时间, 结束时间, cell, eventID]
        self.dangerDict = dict()
        # 以车道id为索引, 记录[开始时间, 结束时间, lane, eventID]
        self.crowdDict = dict()

    def _initTimePropertiesUnitTrans2Frames(self):
        '''function _initTimePropertiesUnitTrans2Frames

        初始化时间属性单位转换为帧。因采用timestamp而弃用。
        '''
        timeProperties = [
            'tTolerance', 'WarnFreq', 'durationStop', 'durationLowSpeed',
            'durationHighSpeed', 'durationEmgcBrake', 'tSupervise',
            'durationIllegalOccupation']
        for param in timeProperties:
            self.__setattr__(param, self.__getattribute__(param) * self.fps)

    def run(self, cars: list) -> dict:
        ''' function run

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        更新交通流信息, 检测交通事件, 输出并返回事件列表。
        '''
        # 清空上一帧事件信息
        self.currentIDs = []
        self.eventMng.clear()   # 清空事件管理器
        # 更新交通流信息
        self.update(cars)
        # 检测交通事件
        self.updatePotentialDict(cars)
        self.detect(cars)
        return self.eventMng.events

    def updatePotentialDict(self, cars: list) -> None:
        '''function updatePotentialDict

        更新潜在事件记录变量, 将对应车辆的id和持续帧数记录在字典中。
        潜在事件包括: 静止, 低速, 超速, 急刹车, 非法占道。
        负责上报事件结束。
        '''
        # 1.遍历车辆
        # 更新当前帧车辆id列表, 检测潜在事件
        for car in cars:
            # 加入当前帧id列表
            self.currentIDs.append(car['id'])
            # 检车车辆可能产生的潜在事件
            for type in self.potentialEventTypes:
                # 该类别事件未发生则跳过
                if not (getattr(self, f'_isCar{strCapitalize(type)}')(car)):
                    continue
                # 事件发生
                if car['id'] not in getattr(self, f'{type}Dict').keys():
                    # 未有该车记录, 该事件首次出现
                    getattr(self, f'{type}Dict')[car['id']] = \
                        [car['timestamp'], car['timestamp'], car, '']
                else:
                    # 已有该车记录, 该事件已出现过, 更新该事件的当前时间和车辆信息
                    getattr(self, f'{type}Dict')[car['id']][1] = \
                        car['timestamp']
                    getattr(self, f'{type}Dict')[car['id']][2] = \
                        car
        # 2. 遍历潜在事件记录字典
        # 删除无效dict键, 包括当前帧丢失目标, 或未消失但已脱离事件检测条件的目标
        for type in self.potentialEventTypes:
            self._deleteNoUsePotentialDictKeys(type, cars)

    def detect(self, cars: list):
        '''function detect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测交通事件, 输出并返回事件列表。负责上报事件开始。
        部分检测子函数中, cars仅用于为报警事件提供信息。
        '''
        for event_type in self.eventTypes:
            getattr(self, f'_{event_type}Detect')(cars)

    def _spillDetect(self, cars: list):
        '''function spillDetect

        input
        ------
        cars: list, 传感器数据, 仅用作统一与其他detect的输入格式

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测抛洒物事件, 输出并返回事件列表
        '''
        # 设备信息
        deviceID = cars[0]['deviceID']
        deviceType = cars[0]['deviceType']
        self.updateDanger()     # 更新危险度
        # 检查是否存在抛洒物可能
        for id in self.lanes:
            for order in self.lanes[id].cells:
                if self.lanes[id].cells[order].danger < 1:
                    continue    # 危险度小于1, 跳过
                # 记录
                if (id, order) not in self.dangerDict.keys():
                    self.dangerDict[(id, order)] = \
                        [cars[0]['timestamp'], cars[0]['timestamp'],
                            self.lanes[id].cells[order], '']
                else:       # 若已记录, 更新记录的当前时间和cell
                    self.dangerDict[(id, order)][1] = cars[0]['timestamp']
                    self.dangerDict[(id, order)][2] = \
                        self.lanes[id].cells[order]
                # 报警
                deltaTms = self.dangerDict[(id, order)][1] - \
                    self.dangerDict[(id, order)][0]
                deltaTs = deltaTms / 1000
                if (deltaTs % self.WarnFreq) <= (1 / self.fps) * 0.9:
                    # 生成事件
                    eventID = self.eventMng.run(
                        'spill', self.dangerDict[(id, order)][0], -1,
                        self.dangerDict[(id, order)][2],
                        deviceID, deviceType, self.dangerDict[(id, order)][3])
                    self.dangerDict[(id, order)][3] = eventID
                    # 生成log信息
                    cellStart = self.lanes[id].cells[order].start
                    cellEnd = self.lanes[id].cells[order].end
                    if cellStart >= cellEnd:
                        cellStart, cellEnd = cellEnd, cellStart
                    startTime = unixMilliseconds2Datetime(
                        self.dangerDict[(id, order)][0])
                    endTime = unixMilliseconds2Datetime(
                        self.dangerDict[(id, order)][1])
                    logEvent = f"事件ID={eventID} - " +\
                        f"id={id}车道可能有抛洒物, " + \
                        f"元胞起点: {cellStart}, 元胞终点: {cellEnd}, " + \
                        f"危险度: {self.lanes[id].cells[order].danger}, " + \
                        f"开始时间: {startTime}, " + \
                        f"当前时间: {endTime}"
                    self.logger.warning(logEvent)

                else:   # 未达到1, 检查是否在记录表内, 若在则删除
                    if (id, order) in self.dangerDict.keys():
                        # 生成结束事件告警
                        eventID = self.eventMng.run(
                            'spill',
                            self.dangerDict[(id, order)][0],
                            self.dangerDict[(id, order)][1],
                            self.dangerDict[(id, order)][2],
                            deviceID, deviceType,
                            self.dangerDict[(id, order)][3])
                        # 生成log信息
                        cellStart = self.lanes[id].cells[order].start
                        cellEnd = self.lanes[id].cells[order].end
                        if cellStart >= cellEnd:
                            cellStart, cellEnd = cellEnd, cellStart
                        startTime = unixMilliseconds2Datetime(
                            self.dangerDict[(id, order)][0])
                        endTime = unixMilliseconds2Datetime(
                            self.dangerDict[(id, order)][1])
                        logEvent = f"事件ID={eventID} - " +\
                            f"id={id}车道抛洒物已处理, " + \
                            f"元胞起点: {cellStart}, 元胞终点: {cellEnd}, " + \
                            f"危险度: {self.lanes[id].cells[order].danger}, " + \
                            f"开始时间: {startTime}, " + \
                            f"结束时间: {endTime}"
                        self.logger.warning(logEvent)
                        del self.dangerDict[(id, order)]

        self.resetCellDetermineStatus()

    def _singleCarEventDetect(self, cars: list, eventType: str):
        '''function singleCarEventDetect

        input
        ------
        cars: list, 传感器数据
        eventType: str, 事件类型

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测单车事件, 输出并返回事件列表
        '''
        eventRecordDict = getattr(self, eventType+'Dict')
        threshold = getattr(self, 'duration'+strCapitalize(eventType))
        for id in eventRecordDict:
            # 检查事件
            deltaTms = eventRecordDict[id][1] - eventRecordDict[id][0]
            deltaTs = deltaTms / 1000
            condition1 = deltaTs > threshold
            condition2 = eventRecordDict[id][3] == ''
            # 生成事件
            if condition1 and condition2:
                # 告警
                car = getCarFromCars(cars, id)
                eventID = self.eventMng.run(
                    eventType, eventRecordDict[id][0], -1,
                    car, eventRecordDict[id][3])
                eventRecordDict[id][3] = eventID
                # 生成log信息
                startTime = unixMilliseconds2Datetime(eventRecordDict[id][0])
                logEvent = f"事件ID={eventID} - " +\
                    f"id={str(id)}车辆发生{eventType}, " + getCarBaseInfo(car) + \
                    f", 开始时间{startTime}."
                self.logger.warning(logEvent)

    def _stopDetect(self, cars: list):
        '''function stopDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测低速事件, 输出并返回事件列表
        '''
        self._singleCarEventDetect(cars, 'stop')

    def _lowSpeedDetect(self, cars: list):
        '''function lowSpeedDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测低速事件, 输出并返回事件列表
        '''
        self._singleCarEventDetect(cars, 'lowSpeed')

    def _highSpeedDetect(self, cars: list):
        '''function highSpeedDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测超速事件, 输出并返回事件列表
        '''
        self._singleCarEventDetect(cars, 'highSpeed')

    def _emgcBrakeDetect(self, cars: list):
        '''function intensiveSpeedReductionDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测急刹车事件, 输出并返回事件列表。减速判断也需要考虑加速度a方向需要跟v方向相反。
        '''
        self._singleCarEventDetect(cars, 'emgcBrake')

    def _illegalOccupationDetect(self, cars: list):
        '''function illegalOccupationDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测非法占道事件, 输出并返回事件列表
        '''
        self._singleCarEventDetect(cars, 'illegalOccupation')

    def _incidentDetect(self, cars: list):
        '''function incidentDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测多车事故事件, 输出并返回事件列表
        '''
        # 异常运动车辆少于2, 不可能有事故
        if (len(self.stopDict) + len(self.lowSpeedDict) +
                len(self.highSpeedDict) + len(self.emgcBrakeDict)) < 2:
            return
        # 更新事故监测记录字典
        self._updateIncidentDict(cars)
        # 遍历incidentDict, 检查事件
        key2delete = []  # 用于缓存应当删除的键
        for ids in self.incidentDict:
            # 若某一车不在currentIDs中, 则移除监测, 跳过
            if not ((ids[0] in self.currentIDs) &
                    (ids[1] in self.currentIDs)):
                key2delete.append(ids)
                continue
            # 检查两辆车是否在某时刻速度趋于0
            car1 = getCarFromCars(cars, ids[0])
            car2 = getCarFromCars(cars, ids[1])
            # 速度趋于0, 则报警
            if self._isCarStop(car1) & self._isCarStop(car2):
                # 生成事件
                eventID = self.eventMng.run(
                    'incident', self.incidentDict[(car1['id'], car2['id'])],
                    car1['timestamp'], car1, car2)
                logEvent = f"事件ID={eventID} - " +\
                    f"id={str(ids[0])},{str(ids[1])}车辆碰撞, " + \
                    getCarBaseInfo(car1) + getCarBaseInfo(car2)
                self.logger.warning(logEvent)
                # 删除记录
                key2delete.append(ids)
            else:   # 碰撞后的过程, 速度下降但未趋于0时, 计数
                self.incidentDict[ids] += 1
                # 检查是否超过监测时间
                deltaTms = car1['timestamp'] - self.incidentDict[ids]
                deltaTs = deltaTms / 1000
                if deltaTs > self.tSupervise:
                    # 删除记录
                    key2delete.append(ids)
        # 删除不需监测的键
        delDictKeys(self.incidentDict, key2delete)

    def _updateIncidentDict(self, cars: list):
        '''function updateIncidentDict

        input
        ------
        cars: list, 传感器数据

        用于更新事故监测记录字典, 用于监测多车事故。
        为_incidentDetect子函数。
        '''
        # 组合异常车辆id列表, 求并集
        abIDs = set(self.stopDict.keys()) | set(self.lowSpeedDict.keys()) |\
            set(self.highSpeedDict.keys()) | set(self.emgcBrakeDict.keys())
        # 利用集合运算, 删除不在currentIDs中的id
        abIDs = abIDs & set(self.currentIDs)
        abIDs = list(abIDs)
        # 两两组合记录潜在事件
        for i in range(len(abIDs)):
            for j in range(i+1, len(abIDs)):
                # 获取车辆
                car1 = getCarFromCars(cars, abIDs[i])
                car2 = getCarFromCars(cars, abIDs[j])
                # 判定非拥堵情况(拥堵情况跳过判断)
                kLane1 = self.lanes[car1['laneID']].k
                kLane2 = self.lanes[car2['laneID']].k
                kAve = (kLane1 + kLane2) / 2
                vLane1 = self.lanes[car1['laneID']].v
                vLane2 = self.lanes[car2['laneID']].v
                vAve = (vLane1 + vLane2) / 2
                if (kAve < self.densityCrowd) & (vAve > self.vCrowd):
                    continue
                # 判定距离小于接触距离
                d = ((car1['x'] - car2['x'])**2 +
                     (car1['y'] - car2['y'])**2)**0.5
                if d < self.dTouch:  # 加入监测对象
                    idsIn = (car1['id'], car2['id']) not in \
                        self.incidentDict.keys()
                    # 如果未在监测对象中, 则添加
                    if idsIn:
                        self.incidentDict[(car1['id'], car2['id'])] = \
                            car1['timestamp']

    def _crowdDetect(self, cars: list) -> list:
        '''function crowdDetect

        input
        ------
        cars: list, 传感器数据, 仅用作统一与其他detect的输入格式

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测拥堵事件, 输出并返回事件列表
        '''
        # 获取设备信息
        deviceID = cars[0]['deviceID']
        deviceType = cars[0]['deviceType']
        # 遍历车道实例
        for id in self.lanes:
            k = self.lanes[id].k
            v = self.lanes[id].v
            # 检查事件
            if (k >= self.densityCrowd) & (v <= self.vCrowd):
                # 记录到dict
                if id not in self.crowdDict.keys():
                    # 若未曾记录, 添加记录
                    self.crowdDict[id] = [cars[0]['timestamp'],
                                          cars[0]['timestamp'],
                                          self.lanes[id], '']
                else:
                    # 若已记录, 更新记录的当前时间和lane
                    self.crowdDict[id][1] = cars[0]['timestamp']
                    self.crowdDict[id][2] = self.lanes[id]
                deltaTms = self.crowdDict[id][1] - self.crowdDict[id][0]
                deltaTs = deltaTms / 1000
                # 报警
                if deltaTs % self.WarnFreq <= (1 / self.fps) * 0.9:
                    # 生成事件
                    eventID = self.eventMng.run(
                        'crowd', cars[0]['timestamp'], -1,
                        self.lanes[id], deviceID, deviceType,
                        self.crowdDict[id][3])
                    self.crowdDict[id][3] = eventID
                    logEvent = f"事件ID={eventID}:" +\
                        f": id={id}车道拥堵, 车道密度: {k}辆/km, 车道速度: {v}km/h."
                    self.logger.warning(logEvent)

            else:   # 不满足拥堵条件, 检查是否在记录表内, 若在则删除
                if id in self.crowdDict.keys():
                    # 生成结束event
                    eventID = self.eventMng.run(
                        'crowd', self.crowdDict[id][0],
                        self.crowdDict[id][1], self.crowdDict[id][2],
                        deviceID, deviceType, self.crowdDict[id][3])
                    logEvent = f"事件ID={eventID} - " +\
                        f"id={id}车道拥堵已解除, 车道密度: {k}辆/km, 车道速度: {v}km/h."
                    self.logger.warning(logEvent)
                    del self.crowdDict[id]

    def _isCarStop(self, car: dict) -> bool:
        '''function _isCarStop

        input
        ------
        car: dict, 车辆数据

        output
        ------
        isStop: bool, 是否静止

        判断车辆是否静止
        '''
        return math.sqrt(car['vx']**2 + car['vy']**2) <= self.vStop

    def _isCarLowSpeed(self, car: dict) -> bool:
        '''function _isCarLowSpeed

        input
        ------
        car: dict, 车辆数据

        output
        ------
        isLowSpeed: bool, 是否低速

        判断车辆是否低速
        '''
        return (self.vStop < math.sqrt(car['vx']**2 + car['vy']**2) <=
                self.vLow)

    def _isCarHighSpeed(self, car: dict) -> bool:
        '''function _isCarHighSpeed

        input
        ------
        car: dict, 车辆数据

        output
        ------
        isHighSpeed: bool, 是否高速

        判断车辆是否高速
        '''
        return math.sqrt(car['vx']**2 + car['vy']**2) > self.vHigh

    def _isCarEmgcBrake(self, car: dict) -> bool:
        '''function _isCarEmgcBrake

        input
        ------
        car: dict, 车辆数据

        output
        ------
        isEmgcBrake: bool, 是否急刹车

        判断车辆是否急刹车
        '''
        return ((abs(car['ay']) > self.aEmgcBrake) &
                (car['ay'] * car['vy'] <= 0))

    def _isCarIllegalOccupation(self, car: dict) -> bool:
        '''function _isCarIllegalOccupation

        input
        ------
        car: dict, 车辆数据

        output
        ------
        isIllegalOccupation: bool, 是否非法占用应急车道

        判断车辆是否非法占用应急车道
        '''
        return self.clb[car['laneID']]['emgc']

    def _deleteNoUsePotentialDictKeys(self, type: str, cars: list):
        '''function _deleteNoUsePotentialDictKeys

        input
        ------
        type: str, 潜在事件类型
        cars: list, 传感器数据

        删除无效dict键, 包括当前帧丢失目标, 或未消失但已脱离事件检测条件的目标。
        注意: dict键记录的只是潜在事件, 可能有些id车辆并未发生该事件。
        '''
        key2delete = []
        # 遍历该类type的dict记录表
        for id in getattr(self, f'{type}Dict').keys():
            # 若该id不在当前帧id列表中, 则删除
            if id not in self.currentIDs:
                key2delete.append(id)
                continue
            # 若该id车辆已经脱离了交通事件的条件, 则删除
            car = getCarFromCars(cars, id)
            if not getattr(self, f'_isCar{strCapitalize(type)}')(car):
                key2delete.append(id)
        # 遍历key2delete, 生成结束event, 删除无效keys
        for key in key2delete:
            # 生成结束event
            dictInfo = getattr(self, f'{type}Dict')[key]
            startTime, endTime = dictInfo[2], dictInfo[3]
            car, eventID = dictInfo[2], dictInfo[3]
            # 潜在事件表中可能有一些车辆并未发生事件
            # 只对已经触发事件报警的车辆生成结束event
            if eventID != '':
                # 告警
                eventID = self.eventMng.run(
                    type, startTime, endTime, car, eventID)
                # 生成log信息
                startTime = unixMilliseconds2Datetime(startTime)
                endTime = unixMilliseconds2Datetime(endTime)
                logEvent = f"事件ID={eventID} - " +\
                    f"id={key}车辆{type}事件结束, " + getCarBaseInfo(car) +\
                    f", 开始时间{startTime}, 结束时间{endTime}."
                self.logger.warning(logEvent)
            # 删除所有无效keys
            del getattr(self, f'{type}Dict')[key]
