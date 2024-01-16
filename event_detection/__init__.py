from traffic_manager import TrafficMng


default_event_types = ['crowd', 'high_speed', 'illegal_occupation',
                       'incident_single_car', 'incident',
                       'intensive_speed_reduction', 'low_speed', 'spill']


class EventDetector(TrafficMng):
    '''class EventDetector

    Properties
    ----------
    fps: float
        frequency per second, 传感器采样频率
    config: dict
        检测参数，包括: vl, vh, tt, r2, dt, dstc, vc, ai, di, dl, dh。
        vl: float, v_low, 低速阈值, 单位m/s
        vh: float, v_high, 高速阈值, 单位m/s
        tt: float, t_tolerance, 事件持续时间容忍度, 单位s
        r2: float, rate2, 抛洒物横向运动置信度增长率
        dt: float, d_touch, 车辆碰撞判定距离, 单位m
        dstc: float, density_crowd, 拥堵密度阈值, 单位辆/km
        vc: float, v_crowd, 拥堵速度阈值, 单位m/s
        ai: float, a_intense, 急刹车加速度阈值(绝对值), 单位m/s^2
        di: float, duration_intense, 急刹车持续时间阈值, 单位s
        dl: float, duration_low, 低速持续时间阈值, 单位s
        dh: float, duration_high, 高速持续时间阈值, 单位s
    types: list
        event_types需要检测的事件列表。default=['crowd', 'high_speed',
        'illegal_occupation', 'incident_single_car', 'incident',
        'intensive_speed_reduction', 'low_speed', 'spill']

    事件检测类, 用于检测交通事件。继承TrafficMng类, 用于获取交通流信息。
    此种定义下, 在外围调用时, 无需生成TrafficMng类, 
    只需生成EventDetector类即可, EventDetector可直接调用TrafficMng的方法。
    '''
    def __init__(self, fps, clb, cfg, event_types=default_event_types,
                 vl: float = 2.778, vh: float = 33.33,
                 tt: float = 300, qs: float = 10000,
                 r2: float = 0.1, dt: float = 5,
                 dstc: float = 18, vc: float = 16.67,
                 ai: float = 3, di: float = 1,
                 dl: float = 5, dh: float = 5):
        ''' function __init__

        input
        ------
        fps: float
            frequency per second, 传感器采样频率

        event_types: list
            需要检测的事件列表。
        vl: float
            v_low, 低速阈值, 单位m/s
        vh: float
            v_high, 高速阈值, 单位m/s
        tt: float
            t_tolerance, 事件持续时间容忍度, 单位s
        qs: float
            q standard, 标准情况的道路通行流量, 单位v/h
        r2: float
            rate2, 抛洒物横向运动置信度增长率
        dt: float
            d_touch, 车辆碰撞判定距离, 单位m
        dstc: float
            density_crowd, 拥堵密度阈值, 单位辆/km
        vc: float
            v_crowd, 拥堵速度阈值, 单位m/s
        ai: float
            a_intense, 急刹车加速度阈值(绝对值), 单位m/s^2
        di: float
            duration_intense, 急刹车持续时间阈值, 单位s
        dl: float
            duration_low, 低速持续时间阈值, 单位s
        dh: float
            duration_high, 高速持续时间阈值, 单位s

        生成事件检测器，用于检测交通事件。
        '''
        # TODO 将eventdetector的初始化调整成适应接收clg和cfg的形式
        # TODO 检查tfm和ed是否有相同命名冲突
        # TODO 重命名config属性为cfg
        # TODO 将各种检测函数调整为类的方法
        # TODO 在外层要将所有trafficmanager的方法都调整为由eventdetector调用
        # TODO 为eventdetector设置一个新的run方法，用于更新交通数据和检测事件
        # 令TrafficMng方法初始化给自身
        super().__init__(clb, cfg)
        self.fps = fps
        self.config = {'vl': vl, 'vh': vh, 'tt': tt, 'qs': qs, 'r1': 1/tt,
                       'r2': r2, 'dt': dt, 'dstc': dstc, 'vc': vc,
                       'ai': ai, 'di': di, 'dl': dl, 'dh': dh}
        self.types = event_types

    def run(self, msg: list) -> list:
        ''' function run

        input
        ------
        msg: list
            传感器数据

        output
        ------
        events: list
            事件列表, 元素为event的衍生类

        更新交通流信息, 检测交通事件, 输出并返回事件列表。
        '''
        # 更新交通流信息
        self.update(msg)    # TODO 待定
        # 检测交通事件
        events = self.detect(msg)
        return events

    def detect(self, msg: list) -> list:
        '''
        检测交通事件，输出并返回事件列表
        input
        ------
        msg: list
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
        # 直接数值检测
        if 'crowd' in self.types:
            events_c = self.crowdDetect()
            events += events_c
        # 群体性检测
        if 'incident' in self.types:
            events_i = self.incidentDetect(msg)
            events += events_i
        if 'spill' in self.types:
            events_s = self.spillDetect()
            events += events_s
        # 单体性检测
        if 'high_speed' in self.types:
            events_h = self.highSpeedDetect(msg)
            events += events_h
        if 'illegal_occupation' in self.types:
            events_o = self.illegalOccupationDetect(msg)
            events += events_o
        if 'incident_single_car' in self.types:
            events_is = self.incidentSingleCarDetect(msg)
            events += events_is
        if 'intensive_speed_reduction' in self.types:
            events_r = self.SuddenBrakingDetect(msg)
            events += events_r
        if 'low_speed' in self.types:
            events_l = self.lowSpeedDetect(msg)
            events += events_l

        return events

    def crowdDetect(self) -> list:
        '''function crowdDetect

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测拥堵事件，输出并返回事件列表
        '''
        events_c = []

        return events_c

    def highSpeedDetect(self, msg: list) -> list:
        '''function highSpeedDetect

        input
        ------
        msg:
            list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测超速事件, 输出并返回事件列表
        '''
        events_h = []

        return events_h

    def illegalOccupationDetect(self, msg: list) -> list:
        '''function illegalOccupationDetect

        input
        ------
        msg:
            list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测非法占用应急车道事件, 输出并返回事件列表
        '''
        events_o = []

        return events_o

    
    def incidentSingleCarDetect(self, msg: list) -> list:
        '''function incidentSingleCarDetect

        input
        ------
        msg:
            list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测单车事故事件, 输出并返回事件列表
        '''
        events_is = []

        return events_is

    def incidentDetect(self, msg: list) -> list:
        '''function incidentDetect

        input
        ------
        msg:
            list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测多车事故事件, 输出并返回事件列表
        '''
        events_i = []

        return events_i

    
    def lowSpeedDetect(self, msg: list) -> list:
        '''function lowSpeedDetect

        input
        ------
        msg:
            list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测低速事件, 输出并返回事件列表
        '''
        events_l = []

        return events_l

    
    def spillDetect(self) -> list:
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

    
    def SuddenBrakingDetect(self, msg: list) -> list:
        '''function intensiveSpeedReductionDetect

        input
        ------
        msg:
            list, 传感器数据

        output
        ------
        events: list, 事件列表, 元素为event的衍生类

        检测急刹车事件, 输出并返回事件列表。减速判断也需要考虑加速度a方向需要跟v方向相反。
        '''
        events_r = []

        return events_r
