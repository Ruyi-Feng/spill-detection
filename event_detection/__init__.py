from traffic_manager import TrafficMng
from utils import updateDictCount, delDictKeys
from utils.car_utils import getCarFromCars, getCarBaseInfo


'''The module is to detect events. Params are defined in config.json.'''


class EventDetector(TrafficMng):
    '''class EventDetector

    事件检测类, 用于检测交通事件。继承TrafficMng类, 用于获取交通流信息。
    唯一对外调用函数: `run(cars)`, 用于更新交通流信息, 检测交通事件, 输出并返回事件列表。
    此种定义下, 在外围调用时, 无需生成TrafficMng类,
    只需生成EventDetector类即可, EventDetector可直接调用TrafficMng的方法。
    TODO 当前报警信息每帧输出一次, 没必要, 除spill外报警一次即可。

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
    vStatic:        float, 准静止判定速度阈值, 单位m/s
    durationStatic: float, 准静止持续时间阈值, 单位s
    vLow:           float, 低速阈值, 单位m/s
    durationLow:    float, 低速持续时间阈值, 单位s
    vHigh:          float, 高速阈值, 单位m/s
    durationHigh:   float, 高速持续时间阈值, 单位s
    aIntense:       float, 急刹车加速度阈值(绝对值), 单位m/s^2
    durationIntense: float, 急刹车持续时间阈值, 单位s
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

        生成事件检测器，用于检测交通事件。
        '''
        # 令TrafficMng方法初始化给自身
        super().__init__(clb, cfg)
        # 初始化属性(其中秒为单位属性, 统一初次赋值后, 乘fps以帧为单位)
        self.clb = clb
        self.fps = cfg['fps']
        for param in cfg:
            self.__setattr__(param, cfg[param])

        # 更新参数单位从秒到帧
        self.tTolerance *= self.fps             # 抛洒物存在持续时间容忍度
        self.spillWarnFreq *= self.fps          # 抛洒物报警频率
        self.durationStatic *= self.fps         # 准静止持续时间阈值
        self.durationLow *= self.fps            # 低速持续时间阈值
        self.durationHigh *= self.fps           # 高速持续时间阈值
        self.durationIntense *= self.fps        # 急刹车持续时间阈值
        self.tSupervise *= self.fps             # 车辆碰撞监控时间
        self.durationOccupation *= self.fps     # 非法占道持续时间阈值

        # 初始化潜在事件记录变量
        self.currentIDs = []    # 当前帧车辆id列表
        # 记录数据格式为: {车辆id: 持续帧数count}
        self.staticDict = dict()
        self.lowSpeedDict = dict()
        self.highSpeedDict = dict()
        self.intenseDict = dict()
        self.occupationDict = dict()
        # 高级记录器, 记录事故监测
        self.incidentDict = dict()  # 以两辆车id为索引, 记录监测时间
        # 高级记录器，记录抛洒物监测
        self.dangerDict = dict()    # 以车道id+cell order为索引, 记录持续帧数

    def run(self, cars: list) -> list:
        ''' function run

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        更新交通流信息, 检测交通事件, 输出并返回事件列表。
        '''
        # 更新交通流信息
        self.update(cars)
        # 检测交通事件
        self.updatePotentialDict(cars)
        events = self.detect(cars)
        self.currentIDs = []    # 清空当前帧车辆id列表
        return events

    def updatePotentialDict(self, cars: list) -> None:
        '''function updatePotentialDict

        更新潜在事件记录变量, 将对应车辆的id和持续帧数记录在字典中。
        潜在事件包括: 静止, 低速, 超速, 急刹车, 非法占道。
        关于为啥这个函数套了5个小函数, 因为直接写在这个里面flake8会提示复杂了。
        '''
        # 遍历车辆
        for car in cars:
            # 加入当前帧id列表
            self.currentIDs.append(car['id'])
            # 潜在静止
            if abs(car['vy']) <= self.vStatic:
                updateDictCount(self.staticDict, car['id'])
            # 潜在低速
            if self.vStatic < abs(car['vy']) <= self.vLow:
                updateDictCount(self.lowSpeedDict, car['id'])
            # 潜在超速
            if abs(car['vy']) > self.vHigh:
                updateDictCount(self.highSpeedDict, car['id'])
            # 潜在急刹车
            # TODO a可能要考虑改为ax,ay,a
            if (abs(car['a']) > self.aIntense) & (car['a'] * car['vy'] <= 0):
                updateDictCount(self.intenseDict, car['id'])
            # 潜在应急车道占用
            if self.clb[car['laneID']]['emgc']:
                updateDictCount(self.occupationDict, car['id'])

    def detect(self, cars: list) -> list:
        '''function detect

        检测交通事件，输出并返回事件列表。
        部分检测子函数中, cars仅用于为报警事件提供信息。
        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类
        '''
        events = []
        for event_type in self.eventTypes:
            events += getattr(self, f'_{event_type}Detect')(cars)
        return events

    def _spillDetect(self, cars: list) -> list:
        '''function spillDetect

        input
        ------
        cars: list, 传感器数据, 仅用作统一与其他detect的输入格式

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测抛洒物事件, 输出并返回事件列表
        '''
        events_s = []
        self.updateDanger()     # 更新危险度
        # 检查是否存在抛洒物可能
        for id in self.lanes:
            for order in self.lanes[id].cells:
                # 检查危险度达到1否, 若则报警
                if self.lanes[id].cells[order].danger >= 1:
                    # 记录
                    if (id, order) in self.dangerDict.keys():
                        self.dangerDict[(id, order)] += 1
                    else:
                        self.dangerDict[(id, order)] = 1
                    # 报警
                    if self.dangerDict[(id, order)] % self.spillWarnFreq == 0:
                        cellStart = self.lanes[id].cells[order].start
                        cellEnd = self.lanes[id].cells[order].end
                        if cellStart >= cellEnd:
                            cellStart, cellEnd = cellEnd, cellStart
                        event = f"事件: id={id}车道可能有抛洒物, " + \
                            f"元胞起点: {cellStart}, 元胞终点: {cellEnd}, " + \
                            f"危险度: {self.lanes[id].cells[order].danger}, " + \
                            f"持续时间: {self.dangerDict[(id, order)]/self.fps}s。"
                        events_s.append(event)
                else:   # 未达到1, 检查是否在记录表内, 若在则删除
                    if (id, order) in self.dangerDict.keys():
                        del self.dangerDict[(id, order)]

        return events_s

    def _stopDetect(self, cars: list) -> list:
        '''function stopDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测低速事件, 输出并返回事件列表
        '''
        events_l = []
        id2delete = []  # 用于缓存已消失的目标id
        for id in self.staticDict.keys():
            # 检查目标是否已消失
            if id not in self.currentIDs:
                id2delete.append(id)
                continue
            # 检查事件
            if self.staticDict[id] == self.ds:
                event = f"事件: id={str(id)}车辆准静止, " + \
                    getCarBaseInfo(getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.staticDict[id]/self.fps)}s。"
                events_l.append(event)
        # 删除已消失目标
        delDictKeys(self.staticDict, id2delete)
        return events_l

    def _lowSpeedDetect(self, cars: list) -> list:
        '''function lowSpeedDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测低速事件, 输出并返回事件列表
        '''
        events_l = []
        id2delete = []  # 用于缓存已消失的目标id
        for id in self.lowSpeedDict.keys():
            # 检查目标是否已消失
            if id not in self.currentIDs:
                id2delete.append(id)
                continue
            # 检查事件
            if self.lowSpeedDict[id] == self.durationLow:
                event = f"事件: id={str(id)}车辆低速行驶, " + \
                    getCarBaseInfo(getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.lowSpeedDict[id]/self.fps)}s。"
                events_l.append(event)
        # 删除已消失目标
        delDictKeys(self.lowSpeedDict, id2delete)
        return events_l

    def _highSpeedDetect(self, cars: list) -> list:
        '''function highSpeedDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测超速事件, 输出并返回事件列表
        '''
        events_h = []
        id2delete = []  # 用于缓存已消失的目标id
        for id in self.highSpeedDict.keys():
            # 检查目标是否已消失
            if id not in self.currentIDs:
                id2delete.append(id)
                continue
            # 检查事件
            if self.highSpeedDict[id] == self.durationHigh:
                event = f"事件: id={str(id)}车辆超速行驶, " + \
                    getCarBaseInfo(getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.highSpeedDict[id]/self.fps)}s。"
                events_h.append(event)
        # 删除已消失目标
        delDictKeys(self.highSpeedDict, id2delete)
        return events_h

    def _emergencyBrakeDetect(self, cars: list) -> list:
        '''function intensiveSpeedReductionDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测急刹车事件, 输出并返回事件列表。减速判断也需要考虑加速度a方向需要跟v方向相反。
        '''
        events_r = []
        id2delete = []  # 用于缓存已消失的目标id
        for id in self.intenseDict.keys():
            # 检查目标是否已消失
            if id not in self.currentIDs:
                id2delete.append(id)
                continue
            # 检查事件
            if self.intenseDict[id] == self.durationIntense:
                event = f"事件: id={str(id)}车辆急刹车, " + \
                    getCarBaseInfo(getCarFromCars(cars, id)) + \
                    f"加速度: {cars[id]['a']}" + \
                    f", 已持续时间{str(self.intenseDict[id]/self.fps)}s。"
                events_r.append(event)
        # 删除已消失目标
        delDictKeys(self.intenseDict, id2delete)
        return events_r

    def _incidentDetect(self, cars: list) -> list:
        '''function incidentDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测多车事故事件, 输出并返回事件列表
        '''
        events_i = []
        # 异常运动车辆少于2，不可能有事故
        if (len(self.staticDict) + len(self.lowSpeedDict) +
                len(self.highSpeedDict) + len(self.intenseDict)) < 2:
            return events_i
        # 组合异常车辆id列表, 求并集
        abIDs = set(self.staticDict.keys()) | set(self.lowSpeedDict.keys()) |\
            set(self.highSpeedDict.keys()) | set(self.intenseDict.keys())
        # 利用集合运算，删除不在currentIDs中的id
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
            if ((abs(car1['vy']) <= self.vStatic) &
               (abs(car2['vy']) <= self.vStatic)):
                event = f"事件: id={str(ids[0])},{str(ids[1])}车辆碰撞, " + \
                    getCarBaseInfo(car1) + getCarBaseInfo(car2)
                events_i.append(event)
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

        return events_i

    def _crowdDetect(self, cars: list) -> list:
        '''function crowdDetect

        input
        ------
        cars: list, 传感器数据, 仅用作统一与其他detect的输入格式

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测拥堵事件，输出并返回事件列表
        '''
        events_c = []
        # 遍历车道实例
        for id in self.lanes:
            k = self.lanes[id].k
            v = self.lanes[id].v
            # 检查事件
            if (k >= self.densityCrowd) & (v <= self.vCrowd):
                event = f"事件: id={id}车道拥堵, 车道密度: {k}辆/km, 车道速度: {v}km/h。"
                events_c.append(event)
        return events_c

    def _illegalOccupationDetect(self, cars: list) -> list:
        '''function illegalOccupationDetect

        input
        ------
        cars: list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测非法占用应急车道事件, 输出并返回事件列表
        '''
        events_o = []
        id2delete = []  # 用于缓存已消失的目标id
        for id in self.occupationDict.keys():
            # 检查目标是否已消失
            if id not in self.currentIDs:
                id2delete.append(id)
                continue
            # 检查事件
            if self.occupationDict[id] == self.durationOccupation:
                event = f"事件: id={str(id)}车辆非法占用应急车道, " + \
                    getCarBaseInfo(getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.occupationDict[id]/self.fps)}s。"
                events_o.append(event)
        # 删除已消失目标
        delDictKeys(self.occupationDict, id2delete)
        return events_o
