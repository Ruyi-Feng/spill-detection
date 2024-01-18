from traffic_manager import TrafficMng


default_event_types = ['spill',
                       'stop', 'low_speed', 'high_speed', 'emergency_break',
                       'incident', 'crowd', 'illegal_occupation']
# 默认配置适用于高速公路
default_event_config = {'types': default_event_types,
                        'tt': 300, 'qs': 10000, 'r2': 0.1,
                        'vs': 2.778, 'ds': 5, 'vl': 11.11, 'dl': 5,
                        'vh': 33.33, 'dh': 5, 'ai': 3, 'di': 1,
                        'dt': 5, 'ts': 20, 'dstc': 18, 'vc': 16.67, 'do': 5}


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
    types: list
        event_types需要检测的事件列表, 包括: 抛撒物检测,
        停车检测, 低速行驶检测, 超速行驶检测, 急停车检测,
        事故检测, 拥堵检测, 非法占用应急车道检测。

    检测参数，包括: tt, qs, r2, vs, ds, vl, dl, vh, dh, ai, di,
                   dt, ts, dstc, vc, do
    抛洒物检测类
    tt: float, t_tolerance, 事件持续时间容忍度, 单位s
    qs: float, q_standard, 标准情况的道路通行流量, 单位v/h
    r2: float, rate2, 抛洒物横向运动置信度增长率
    异常行驶类
    vs: float, v_static, 准静止判定速度阈值, 单位m/s
    ds: float, duration_static, 准静止持续时间阈值, 单位s
    vl: float, v_low, 低速阈值, 单位m/s
    dl: float, duration_low, 低速持续时间阈值, 单位s
    vh: float, v_high, 高速阈值, 单位m/s
    dh: float, duration_high, 高速持续时间阈值, 单位s
    ai: float, a_intense, 急刹车加速度阈值(绝对值), 单位m/s^2
    di: float, duration_intense, 急刹车持续时间阈值, 单位s
    车辆碰撞检测类
    dt: float, d_touch, 车辆碰撞判定距离, 单位m
    ts: float, t_supervise, 车辆碰撞监控时间, 单位s
    拥堵检测类
    dstc: float, density_crowd, 拥堵密度阈值, 单位辆/km
    vc: float, v_crowd, 拥堵速度阈值, 单位m/s
    非法占道类
    do: float, duration_occupation, 非法占道持续时间阈值, 单位s
    '''
    def __init__(self, fps, clb, cfg):
        ''' function __init__

        input
        ------
        fps: float
            frequency per second, 传感器采样频率
        clb: dict
            已标定的参数字典
        cfg: dict
            配置参数字典
        event_types: list
            需要检测的事件列表

        生成事件检测器，用于检测交通事件。
        '''
        # 令TrafficMng方法初始化给自身
        super().__init__(clb, cfg)
        # 初始化属性(其中秒为单位属性, 统一初次赋值后, 乘fps以帧为单位)
        self.fps = fps
        self.clb = clb
        self.types = cfg['event_types'] if 'event_types' in cfg.keys() else \
            default_event_config['types']
        # 抛洒物检测参数
        self.tt = cfg['tt'] if 't_tolerance' in cfg.keys() else \
            default_event_config['tt']
        self.qs = cfg['qs'] if 'q_standard' in cfg.keys() else \
            default_event_config['qs']
        self.r2 = cfg['r2'] if 'rate2' in cfg.keys() else \
            default_event_config['r2']
        # 异常行驶检测参数
        self.vs = cfg['vs'] if 'v_static' in cfg.keys() else \
            default_event_config['vs']
        self.ds = cfg['ds'] if 'duration_static' in cfg.keys() else \
            default_event_config['ds']
        self.vl = cfg['vl'] if 'v_low' in cfg.keys() else \
            default_event_config['vl']
        self.dl = cfg['dl'] if 'duration_low' in cfg.keys() else \
            default_event_config['dl']
        self.vh = cfg['vh'] if 'v_high' in cfg.keys() else \
            default_event_config['vh']
        self.dh = cfg['dh'] if 'duration_high' in cfg.keys() else \
            default_event_config['dh']
        self.ai = cfg['ai'] if 'a_intense' in cfg.keys() else \
            default_event_config['ai']
        self.di = cfg['di'] if 'duration_intense' in cfg.keys() else \
            default_event_config['di']
        # 车辆碰撞检测参数
        self.dt = cfg['dt'] if 'd_touch' in cfg.keys() else \
            default_event_config['dt']
        self.ts = cfg['ts'] if 't_supervise' in cfg.keys() else \
            default_event_config['ts']
        # 拥堵检测参数
        self.dstc = cfg['dstc'] if 'density_crowd' in cfg.keys() else \
            default_event_config['dstc']
        self.vc = cfg['vc'] if 'v_crowd' in cfg.keys() else \
            default_event_config['vc']
        # 非法占道检测参数
        self.do = cfg['do'] if 'duration_occupation' in cfg.keys() else \
            default_event_config['do']

        # 更新参数单位从秒到帧
        self.tt *= self.fps     # 抛洒物存在持续时间容忍度
        self.ds *= self.fps     # 准静止持续时间阈值
        self.dl *= self.fps     # 低速持续时间阈值
        self.dh *= self.fps     # 高速持续时间阈值
        self.di *= self.fps     # 急刹车持续时间阈值
        self.ts *= self.fps     # 车辆碰撞监控时间
        self.do *= self.fps     # 非法占道持续时间阈值

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

    def run(self, cars: list) -> list:
        ''' function run

        input
        ------
        cars: list
            传感器数据

        output
        ------
        events: list
            事件列表, 元素为event的衍生类

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
            if abs(car['vy']) <= self.vs:
                self._updateStaticDict(car['id'])
            # 潜在低速
            if self.vs < abs(car['vy']) <= self.vl:
                self._updateLowSpeedDict(car['id'])
            # 潜在超速
            if abs(car['vy']) > self.vh:
                self._updateHighSpeedDict(car['id'])
            # 潜在急刹车
            # TODO a可能要考虑改为ax,ay,a
            if (abs(car['a']) > self.ai) & (car['a'] * car['vy'] <= 0):
                self._updateIntenseDict(car['id'])
            # 潜在应急车道占用
            if self.clb[car['laneID']]['emgc']:
                self._updateOccupationDict(car['id'])

    def _updateStaticDict(self, id: int) -> None:
        '''function _updateStaticDict

        input
        ------
        id: int
            车辆id

        更新静止记录字典
        '''
        if id in self.staticDict.keys():
            self.staticDict[id] += 1
        else:
            self.staticDict[id] = 1

    def _updateLowSpeedDict(self, id: int) -> None:
        '''function _updateLowSpeedDict

        input
        ------
        id: int
            车辆id

        更新低速记录字典
        '''
        if id in self.lowSpeedDict.keys():
            self.lowSpeedDict[id] += 1
        else:
            self.lowSpeedDict[id] = 1

    def _updateHighSpeedDict(self, id: int) -> None:
        '''function _updateHighSpeedDict

        input
        ------
        id: int
            车辆id

        更新高速记录字典
        '''
        if id in self.highSpeedDict.keys():
            self.highSpeedDict[id] += 1
        else:
            self.highSpeedDict[id] = 1

    def _updateIntenseDict(self, id: int) -> None:
        '''function _updateIntenseDict

        input
        ------
        id: int
            车辆id

        更新急刹车记录字典
        '''
        if id in self.intenseDict.keys():
            self.intenseDict[id] += 1
        else:
            self.intenseDict[id] = 1

    def _updateOccupationDict(self, id: int) -> None:
        '''function _updateOccupationDict

        input
        ------
        id: int
            车辆id

        更新应急车道占用记录字典
        '''
        if id in self.occupationDict.keys():
            self.occupationDict[id] += 1
        else:
            self.occupationDict[id] = 1

    def detect(self, cars: list) -> list:
        '''function detect

        检测交通事件，输出并返回事件列表。
        部分检测子函数中, cars仅用于为报警事件提供信息。
        input
        ------
        cars: list
            传感器数据

        output
        ------
        events: list
            事件列表, 元素为event的衍生类
        '''

        # 事件检测
        events = []
        # 抛洒物检测
        if 'spill' in self.types:
            events_s = self._spillDetect()
            events += events_s
        # 异常行驶检测
        if 'stop' in self.types:
            events_s = self._stopDetect(cars)
            events += events_s
        if 'low_speed' in self.types:
            events_l = self._lowSpeedDetect(cars)
            events += events_l
        if 'high_speed' in self.types:
            events_h = self._highSpeedDetect(cars)
            events += events_h
        if 'emergency_break' in self.types:
            events_r = self._emergencyBrakeDetect(cars)
            events += events_r
        # 碰撞事故检测
        if 'incident' in self.types:
            events_i = self._incidentDetect(cars)
            events += events_i
        # 拥堵检测
        if 'crowd' in self.types:
            events_c = self._crowdDetect()
            events += events_c
        # 非法占道检测
        if 'illegal_occupation' in self.types:
            events_o = self._illegalOccupationDetect(cars)
            events += events_o
        return events

    def _spillDetect(self) -> list:
        '''function spillDetect

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
                    # TODO 设置每隔一段时间报警, 报警信息包括车道, cell的起始与重点
                    cellStart = self.lanes[id].cells[order].start
                    cellEnd = self.lanes[id].cells[order].end
                    if cellStart >= cellEnd:
                        cellStart, cellEnd = cellEnd, cellStart
                    event = f"事件: id={str(id)}车道可能有抛洒物, " + \
                        f"元胞起点: {str(cellStart)}, 元胞终点: {str(cellEnd)}, " + \
                        f"危险度: {str(self.lanes[id].cells[order].danger)}。"
                    events_s.append(event)
        return events_s

    def _stopDetect(self, cars: list) -> list:
        '''function stopDetect

        input
        ------
        cars:
            list, 传感器数据

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
                    self._getCarBaseInfo(self._getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.staticDict[id]/self.fps)}s。"
                events_l.append(event)
        # 删除已消失目标
        for id in id2delete:
            del self.staticDict[id]
        return events_l

    def _lowSpeedDetect(self, cars: list) -> list:
        '''function lowSpeedDetect

        input
        ------
        cars:
            list, 传感器数据

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
            if self.lowSpeedDict[id] == self.dl:
                event = f"事件: id={str(id)}车辆低速行驶, " + \
                    self._getCarBaseInfo(self._getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.lowSpeedDict[id]/self.fps)}s。"
                events_l.append(event)
        # 删除已消失目标
        for id in id2delete:
            del self.lowSpeedDict[id]
        return events_l

    def _highSpeedDetect(self, cars: list) -> list:
        '''function highSpeedDetect

        input
        ------
        cars:
            list, 传感器数据

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
            if self.highSpeedDict[id] == self.dh:
                event = f"事件: id={str(id)}车辆超速行驶, " + \
                    self._getCarBaseInfo(self._getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.highSpeedDict[id]/self.fps)}s。"
                events_h.append(event)
        # 删除已消失目标
        for id in id2delete:
            del self.highSpeedDict[id]
        return events_h

    def _emergencyBrakeDetect(self, cars: list) -> list:
        '''function intensiveSpeedReductionDetect

        input
        ------
        cars:
            list, 传感器数据

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
            if self.intenseDict[id] == self.di:
                event = f"事件: id={str(id)}车辆急刹车, " + \
                    self._getCarBaseInfo(self._getCarFromCars(cars, id)) + \
                    f"加速度: {cars[id]['a']}" + \
                    f", 已持续时间{str(self.intenseDict[id]/self.fps)}s。"
                events_r.append(event)
        # 删除已消失目标
        for id in id2delete:
            del self.intenseDict[id]
        return events_r

    def _incidentDetect(self, cars: list) -> list:
        '''function incidentDetect

        input
        ------
        cars:
            list, 传感器数据

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
                car1 = self._getCarFromCars(cars, abIDs[i])
                car2 = self._getCarFromCars(cars, abIDs[j])
                # 判定非拥堵情况(拥堵情况跳过判断)
                kLane1 = self.lanes[car1['laneID']].k
                kLane2 = self.lanes[car2['laneID']].k
                kAve = (kLane1 + kLane2) / 2
                vLane1 = self.lanes[car1['laneID']].v
                vLane2 = self.lanes[car2['laneID']].v
                vAve = (vLane1 + vLane2) / 2
                if (kAve < self.dstc) & (vAve > self.vc):
                    continue
                # 判定距离小于接触距离
                d = ((car1['x'] - car2['x'])**2 +
                     (car1['y'] - car2['y'])**2)**0.5
                if d < self.dt:  # 加入监测对象
                    self.incidentDict[[car1['id'], car2['id']]] = 1
        # 遍历incidentDict, 检查事件
        for ids in self.incidentDict:
            # 若某一车不在currentIDs中, 则移除监测, 跳过
            if not ((ids[0] in self.currentIDs) &
                    (ids[1] in self.currentIDs)):
                del self.incidentDict[ids]
                continue
            # 检查两辆车是否在某时刻速度趋于0
            car1 = self._getCarFromCars(cars, ids[0])
            car2 = self._getCarFromCars(cars, ids[1])
            # 速度趋于0, 则报警
            if (abs(car1['vy']) <= self.vs) & (abs(car2['vy']) <= self.vs):
                event = f"事件: id={str(ids[0])},{str(ids[1])}车辆碰撞, " + \
                    self._getCarBaseInfo(car1) + self._getCarBaseInfo(car2)
                events_i.append(event)
                # 删除记录
                del self.incidentDict[ids]
            else:   # 碰撞后的过程, 速度下降但未趋于0时, 计数
                self.incidentDict[ids] += 1
                # 检查是否超过监测时间
                if self.incidentDict[ids] >= self.ts:
                    # 删除记录
                    del self.incidentDict[ids]

        return events_i

    def _crowdDetect(self) -> list:
        '''function crowdDetect

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
            if (k >= self.dstc) & (v <= self.vc):
                event = f"事件: id={id}车道拥堵, 车道密度: {k}辆/km, 车道速度: {v}km/h。"
                events_c.append(event)
        return events_c

    def _illegalOccupationDetect(self, cars: list) -> list:
        '''function illegalOccupationDetect

        input
        ------
        cars:
            list, 传感器数据

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
            if self.occupationDict[id] == self.do:
                event = f"事件: id={str(id)}车辆非法占用应急车道, " + \
                    self._getCarBaseInfo(self._getCarFromCars(cars, id)) + \
                    f", 已持续时间{str(self.occupationDict[id]/self.fps)}s。"
                events_o.append(event)
        # 删除已消失目标
        for id in id2delete:
            del self.occupationDict[id]
        return events_o

    def _getCarFromCars(self, cars: list, id: int) -> dict:
        '''function _getCarFromCars

        input
        ------
        cars: list
            传感器数据
        id: int
            车辆id

        output
        ------
        car: dict
            单车数据

        从传感器数据中获取指定id的单车数据。
        '''
        for car in cars:
            if car['id'] == id:
                return car  # 找到指定id的车辆
        return None     # 未找到指定id的车辆

    def _getCarBaseInfo(self, car: dict) -> str:
        '''function _getCarBaseInfo

        input
        ------
        car: dict
            单车数据

        return
        ------
        info: str
            单车基本信息字符串

        获取单车基本信息字符串, 用于事件信息输出。
        基本信息包括x,y,laneID,vx,vy。
        '''
        info = f"位置(x,y): {round(car['x'], 0)}m, {round(car['y'], 0)}m, " + \
            f"车道号: {car['laneID']}, " + \
            "速度(vx,vy,speed): " + \
            str(round(car['vx'] * 3.6, 0)) + ", " + \
            str(round(car['vy'] * 3.6, 0)) + ", " + \
            str(round(car['speed'] * 3.6, 0)) + "km/h "
        return info
