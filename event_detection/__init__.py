from traffic_manager import TrafficMng
from event_detection.event import EventMng
from utils import updateDictCount, delDictKeys, strCapitalize
from utils.car_utils import getCarFromCars, getCarBaseInfo


'''The module is to detect events. Params are defined in config.json.'''


class EventDetector(TrafficMng):
    '''class EventDetector

    事件检测类, 用于检测交通事件。继承TrafficMng类, 用于获取交通流信息。
    唯一对外调用函数: `run(cars)`, 用于更新交通流信息, 检测交通事件, 输出并返回事件列表。
    此种定义下, 在外围调用时, 无需生成TrafficMng类,
    只需生成EventDetector类即可, EventDetector可直接调用TrafficMng的方法。

    TODO
    1. 单车事件报警, 后续可能需要调整为判定一次+结束一次
    (判定报警已完成, 结束报警应在deleteNoUsePotentialDictKeys中添加)
    2. 肇事事件报警, 只需判定一次即可。因此其dict的记录与操作与其他不同
    3. 抛洒物、拥堵事件报警, 需要判定一次+定期n次, 后续每隔一定时间都要报警一次

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
    spillWarnFreq: int, 抛洒物报警频率, 单位帧
    异常行驶类
    vStop:        float, 准静止判定速度阈值, 单位m/s
    durationStop: float, 准静止持续时间阈值, 单位s
    vLow:           float, 低速阈值, 单位m/s
    durationLow:    float, 低速持续时间阈值, 单位s
    vHigh:          float, 高速阈值, 单位m/s
    durationHigh:   float, 高速持续时间阈值, 单位s
    aEmgcBrake:       float, 急刹车加速度阈值(绝对值), 单位m/s^2
    durationEmgcBrake: float, 急刹车持续时间阈值, 单位s
    车辆碰撞检测类
    dTouch:     float, 车辆碰撞判定距离, 单位m
    tSupervise: float, 车辆碰撞监控时间, 单位s
    拥堵检测类
    densityCrowd: float, 拥堵密度阈值, 单位辆/km
    vCrowd:       float, 拥堵速度阈值, 单位m/s
    非法占道类
    durationOccupation: float, 非法占道持续时间阈值, 单位s
    '''
    def __init__(self, clb, cfg):
        ''' function __init__

        input
        ------
        clb: dict, 已标定的参数字典
        cfg: dict, 配置参数字典
        event_types: list, 需要检测的事件列表

        生成事件检测器, 用于检测交通事件。
        '''
        # 令TrafficMng方法初始化给自身
        super().__init__(clb, cfg)
        # 生成事件管理器
        self.eventMng = EventMng(cfg['eventTypes'])
        # 初始化属性(其中秒为单位属性, 统一初次赋值后, 乘fps以帧为单位)
        self.clb = clb
        self.fps = cfg['fps']
        for param in cfg:
            self.__setattr__(param, cfg[param])

        # 更新参数单位从秒到帧
        self.tTolerance *= self.fps             # 抛洒物存在持续时间容忍度
        self.spillWarnFreq *= self.fps          # 抛洒物报警频率
        self.durationStop *= self.fps         # 准静止持续时间阈值
        self.durationLow *= self.fps            # 低速持续时间阈值
        self.durationHigh *= self.fps           # 高速持续时间阈值
        self.durationEmgcBrake *= self.fps        # 急刹车持续时间阈值
        self.tSupervise *= self.fps             # 车辆碰撞监控时间
        self.durationOccupation *= self.fps     # 非法占道持续时间阈值

        # 初始化潜在事件记录变量
        self.currentIDs = []    # 当前帧车辆id列表
        self.potentialEventTypes = ['stop', 'lowSpeed', 'highSpeed',
                                    'emgcBrake', 'illegalOccupation']
        # 记录数据格式为: {车辆id: 持续帧数count}
        self.stopDict = dict()
        self.lowSpeedDict = dict()
        self.highSpeedDict = dict()
        self.emgcBrakeDict = dict()
        self.illegalOccupationDict = dict()
        # 高级记录器, 记录事故监测
        self.incidentDict = dict()  # 以两辆车id为索引, 记录监测时间
        # 高级记录器, 记录抛洒物监测
        self.dangerDict = dict()    # 以车道id+cell order为索引, 记录持续帧数

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
        '''
        # 1.遍历车辆
        # 更新当前帧车辆id列表, 检测潜在事件
        for car in cars:
            # 加入当前帧id列表
            self.currentIDs.append(car['id'])
            # 检车车辆可能产生的潜在事件
            for type in self.potentialEventTypes:
                if getattr(self, f'_isCar{strCapitalize(type)}')(car):
                    updateDictCount(getattr(self, f'{type}Dict'), car['id'])
        # 2. 遍历潜在事件记录字典
        # 删除无效dict键, 包括当前帧丢失目标, 或未消失但已脱离事件检测条件的目标
        for type in self.potentialEventTypes:
            self._deleteNoUsePotentialDictKeys(type, cars)

    def detect(self, cars: list):
        '''function detect

        检测交通事件, 输出并返回事件列表。
        部分检测子函数中, cars仅用于为报警事件提供信息。
        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类
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
        self.updateDanger()     # 更新危险度
        # 检查是否存在抛洒物可能
        for id in self.lanes:
            for order in self.lanes[id].cells:
                # 检查危险度达到1否, 若则报警
                if self.lanes[id].cells[order].danger >= 1:
                    # 记录
                    updateDictCount(self.dangerDict, (id, order))
                    # 报警
                    if self.dangerDict[(id, order)] % self.spillWarnFreq == 1:
                        cellStart = self.lanes[id].cells[order].start
                        cellEnd = self.lanes[id].cells[order].end
                        if cellStart >= cellEnd:
                            cellStart, cellEnd = cellEnd, cellStart
                        # 调试用输出
                        event = f"事件: id={id}车道可能有抛洒物, " + \
                            f"元胞起点: {cellStart}, 元胞终点: {cellEnd}, " + \
                            f"危险度: {self.lanes[id].cells[order].danger}, " + \
                            f"持续时间: {self.dangerDict[(id, order)]/self.fps}s。"
                        print(event)
                        # 真正用生成事件
                        self.eventMng.run('spill', cars[0]['timestamp'],
                                          self.lanes[id].cells[order])
                else:   # 未达到1, 检查是否在记录表内, 若在则删除
                    if (id, order) in self.dangerDict.keys():
                        del self.dangerDict[(id, order)]
        self.resetCellDetermineStatus()

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
        for id in self.stopDict.keys():
            # 检查事件
            if self.stopDict[id] == self.durationStop:
                car = getCarFromCars(cars, id)
                event = f"事件: id={str(id)}车辆准静止, " + getCarBaseInfo(car) + \
                    f", 已持续时间{str(self.stopDict[id]/self.fps)}s。"
                print(event)
                # 真正用生成事件
                self.eventMng.run('stop', cars[0]['timestamp'], car)

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
        for id in self.lowSpeedDict.keys():
            # 检查事件
            if self.lowSpeedDict[id] == self.durationLow:
                car = getCarFromCars(cars, id)
                event = f"事件: id={str(id)}车辆低速行驶, " + getCarBaseInfo(car) + \
                    f", 已持续时间{str(self.lowSpeedDict[id]/self.fps)}s。"
                print(event)
                # 真正用生成事件
                self.eventMng.run('lowSpeed', cars[0]['timestamp'], car)

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
        for id in self.highSpeedDict.keys():
            # 检查事件
            if self.highSpeedDict[id] == self.durationHigh:
                car = getCarFromCars(cars, id)
                event = f"事件: id={str(id)}车辆超速行驶, " + getCarBaseInfo(car) + \
                    f", 已持续时间{str(self.highSpeedDict[id]/self.fps)}s。"
                print(event)
                # 真正用生成事件
                self.eventMng.run('highSpeed', cars[0]['timestamp'], car)

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
        for id in self.emgcBrakeDict.keys():
            # 检查事件
            if self.emgcBrakeDict[id] == self.durationEmgcBrake:
                car = getCarFromCars(cars, id)
                event = f"事件: id={str(id)}车辆急刹车, " + getCarBaseInfo(car) + \
                    f"加速度: {car['a']}" + \
                    f", 已持续时间{str(self.emgcBrakeDict[id]/self.fps)}s。"
                print(event)
                # 真正用生成事件
                self.eventMng.run('emgcBrake', cars[0]['timestamp'], car)

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
                    updateDictCount(self.incidentDict,
                                    (car1['id'], car2['id']))
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
            if ((abs(car1['vy']) <= self.vStop) &
               (abs(car2['vy']) <= self.vStop)):
                event = f"事件: id={str(ids[0])},{str(ids[1])}车辆碰撞, " + \
                    getCarBaseInfo(car1) + getCarBaseInfo(car2)
                print(event)
                # 真正用生成事件
                self.eventMng.run('incident', cars[0]['timestamp'], car1, car2)
                # 删除记录
                key2delete.append(ids)
            else:   # 碰撞后的过程, 速度下降但未趋于0时, 计数
                self.incidentDict[ids] += 1
                # 检查是否超过监测时间
                if self.incidentDict[ids] >= self.tSupervise:
                    # 删除记录
                    key2delete.append(ids)
        # 删除不需监测的键
        delDictKeys(self.incidentDict, key2delete)

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
        # 遍历车道实例
        for id in self.lanes:
            k = self.lanes[id].k
            v = self.lanes[id].v
            # 检查事件
            if (k >= self.densityCrowd) & (v <= self.vCrowd):
                event = f"事件: id={id}车道拥堵, 车道密度: {k}辆/km, 车道速度: {v}km/h。"
                print(event)
                # 真正用生成事件
                self.eventMng.run('crowd',
                                  cars[0]['timestamp'],
                                  self.lanes[id])

    def _illegalOccupationDetect(self, cars: list):
        '''function illegalOccupationDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测非法占用应急车道事件, 输出并返回事件列表
        '''
        for id in self.illegalOccupationDict.keys():
            # 检查事件
            if self.illegalOccupationDict[id] == self.durationOccupation:
                car = getCarFromCars(cars, id)
                event = f"事件: id={str(id)}车辆占用应急车道, " + getCarBaseInfo(car) +\
                    f", 已持续时间{str(self.illegalOccupationDict[id]/self.fps)}s。"
                print(event)
                # 真正用生成事件
                self.eventMng.run('illegalOccupation',
                                  cars[0]['timestamp'],
                                  car)

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
        return abs(car['speed']) <= self.vStop

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
        return self.vStop < abs(car['speed']) <= self.vLow

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
        return abs(car['speed']) > self.vHigh

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
        TODO 这种情况代表事件已结束, 若需要报警总持续时长, 可在此处添加。
        '''
        key2delete = []
        for id in getattr(self, f'{type}Dict').keys():
            if id not in self.currentIDs:
                key2delete.append(id)
                continue
            car = getCarFromCars(cars, id)
            if not getattr(self, f'_isCar{strCapitalize(type)}')(car):
                key2delete.append(id)
        delDictKeys(getattr(self, f'{type}Dict'), key2delete)
