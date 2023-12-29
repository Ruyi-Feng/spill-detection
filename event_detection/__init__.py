from event_detection.events.crowd import crowdDetect
from event_detection.events.incident import incidentDetect
from event_detection.events.high_speed import highSpeedDetect
from event_detection.events.illegal_occupation import illegalOccupationDetect
from event_detection.events.incident_single_car import incidentSingleCarDetect
from event_detection.events.sudden_braking import SuddenBrakingDetect
from event_detection.events.low_speed import lowSpeedDetect
from event_detection.events.spill import spillDetect


default_event_types = ['crowd', 'high_speed', 'illegal_occupation',
                       'incident_single_car', 'incident',
                       'intensive_speed_reduction', 'low_speed', 'spill']


class EventDetector:
    '''class EventDetector

    Properties
    ----------
    fps: float
        frequency per second, 传感器采样频率
    clb: dict
        标定参数
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


    事件检测类，用于检测交通事件。
    '''
    def __init__(self, fps, clb, event_types=default_event_types,
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
        clb: dict
            标定参数
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
        self.fps = fps
        self.clb = clb
        self.config = {'vl': vl, 'vh': vh, 'tt': tt, 'qs': qs, 'r1': 1/tt,
                       'r2': r2, 'dt': dt, 'dstc': dstc, 'vc': vc,
                       'ai': ai, 'di': di, 'dl': dl, 'dh': dh}
        self.types = event_types

    def run(self, msg, traffic):
        '''
        检测交通事件，输出并返回事件列表
        input
        ------
        msg: list
            传感器数据
        traffic: dict
            交通流数据
        config: dict
            标定参数
        clb: dict
            算法参数
        event_types: list
            需要检测的事件列表。

        output
        ------
        events: list
            事件列表, 元素为event的衍生类
        '''
        # 事件检测
        events = []
        # 直接数值检测
        if 'crowd' in self.types:
            events_c = crowdDetect(traffic,
                                   self.config["dstc"], self.config["vc"])
            events += events_c
        # 群体性检测
        if 'incident' in self.types:
            events_i = incidentDetect(msg, traffic,
                                      self.config, self.clb)
            events += events_i
        if 'spill' in self.types:
            events_s = spillDetect(msg, traffic,
                                   self.config, self.clb)
            events += events_s
        # 单体性检测
        if 'high_speed' in self.types:
            events_h = highSpeedDetect(msg, traffic,
                                       self.config, self.clb)
            events += events_h
        if 'illegal_occupation' in self.types:
            events_o = illegalOccupationDetect(msg, traffic,
                                               self.config, self.clb)
            events += events_o
        if 'incident_single_car' in self.types:
            events_is = incidentSingleCarDetect(msg, traffic,
                                                self.config, self.clb)
            events += events_is

        if 'intensive_speed_reduction' in self.types:
            events_r = SuddenBrakingDetect(msg, traffic,
                                           self.config, self.clb)
            events += events_r
        if 'low_speed' in self.types:
            events_l = lowSpeedDetect(msg, traffic,
                                      self.config, self.clb)
            events += events_l

        return events
