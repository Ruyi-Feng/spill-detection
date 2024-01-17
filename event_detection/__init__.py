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
        # 数据格式为: {车辆id: 持续帧数count}
        self.staticDict = dict()
        self.lowSpeedDict = dict()
        self.highSpeedDict = dict()
        self.intenseDict = dict()
        self.occupationDict = dict()

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
        self.updatePotentialEventDict(cars)
        events = self.detect(cars)
        return events

    def updatePotentialEventDict(self, cars: list) -> None:
        '''function updatePotentialEventDict
        
        更新潜在事件记录变量, 将对应车辆的id和持续帧数记录在字典中。
        潜在事件包括: 静止, 低速, 超速, 急刹车, 非法占道。
        '''
        # 遍历车辆
        for car in cars:
            # 潜在静止
            if abs(car['vy']) <= self.vs:
                if car['id'] not in self.staticDict.keys():
                    self.staticDict[car['id']] = 1
                else:
                    self.staticDict[car['id']] += 1
            # 潜在低速
            if self.vs < abs(car['vy']) <= self.vl:
                if car['id'] not in self.lowSpeedDict.keys():
                    self.lowSpeedDict[car['id']] = 1
                else:
                    self.lowSpeedDict[car['id']] += 1
            # 潜在超速
            if abs(car['vy']) > self.vh:
                if car['id'] not in self.highSpeedDict.keys():
                    self.highSpeedDict[car['id']] = 1
                else:
                    self.highSpeedDict[car['id']] += 1
            # 潜在急刹车
            # TODO a可能要考虑改为ay
            if (abs(car['a']) > self.ai) & (car['a'] * car['vy'] <= 0):
                if car['id'] not in self.intenseDict.keys():
                    self.intenseDict[car['id']] = 1
                else:
                    self.intenseDict[car['id']] += 1
            # 潜在应急车道占用
            if self.clb[car['laneID']]['emgc']:
                if car['id'] not in self.occupationDict.keys():
                    self.occupationDict[car['id']] = 1
                else:
                    self.occupationDict[car['id']] += 1

    def detect(self, cars: list) -> list:
        '''function detect

        检测交通事件，输出并返回事件列表
        input
        ------
        cars: list
            传感器数据
        trf: TrafficMng
            交通管理器, 存有交通流信息

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

        input
        ------
        traffic:
            dict, 交通流数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测抛洒物事件, 输出并返回事件列表
        '''
        events_s = []

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

        return events_i

    def _crowdDetect(self) -> list:
        '''function crowdDetect

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测拥堵事件，输出并返回事件列表
        '''
        events_c = []

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

        return events_o
