default_event_types = ['crowd', 'high_speed', 'illegal_occupation', 'incident_single_car', 
                      'incident', 'intensive_speed_reduction', 'low_speed', 'spill']

class EventDetector:
    def __init__(self, fps, clb, event_types = default_event_types):
        self.config = config
        self.clb = clb
        self.types = event_types
        
    def run(self, msg, traffic):
        '''
        检测交通事件，输出并返回事件列表
        input
        ------
        msg: list, 传感器数据
        traffic: dict, 交通流数据
        config: dict, 标定参数
        clb: dict, 算法参数
        event_types: list, 需要检测的事件列表。

        output
        ------
        events: list, 事件列表, 元素为event的衍生类
        '''
        # 事件检测
        events = []
        if 'crowd' in self.types:
            events_c = crowdDetect(msg, traffic, self.config, self.clb)
            events += events_c
        if 'high_speed' in self.types:
            events_h = highSpeedDetect(msg, traffic, self.config, self.clb)
            events += events_h
        if 'illegal_occupation' in self.types:
            events_o = illegalOccupationDetect(msg, traffic, self.config, self.clb)
            events += events_o
        if 'incident_single_car' in self.types:
            events_is = incidentSingleCarDetect(msg, traffic, self.config, self.clb)
            events += events_is
        if 'incident' in self.types:
            events_i = incidentDetect(msg, traffic, self.config, self.clb)
            events += events_i
        if 'intensive_speed_reduction' in self.types:
            events_r = intensiveSpeedReductionDetect(msg, traffic, self.config, self.clb)
            events += events_r
        if 'low_speed' in self.types:
            events_l = lowSpeedDetect(msg, traffic, self.config, self.clb)
            events += events_l
        if 'spill' in self.types:
            events_s = spillDetect(msg, traffic, self.config, self.clb)
            events += events_s
        
        return events


def crowdDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_c = []

    return events_c


def highSpeedDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_h = []

    return events_h


def illegalOccupationDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_o = []

    return events_o


def incidentSingleCarDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_is = []

    return events_is


def incidentDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_i = []

    return events_i


def intensiveSpeedReductionDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_r = []

    return events_r



def lowSpeedDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_l = []

    return events_l


def spillDetect(msg, traffic, config, clb):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_s = []

    return events_s


class event:
    '''
    事件基础类。不同类型的具体事件以此为基类。
    '''
    def __init__(self, event_name, event_type, event_time, event_location, event_level, event_description):
        self.event_name = event_name
        self.event_type = event_type
        self.event_time = event_time
        self.event_location = event_location
        self.event_level = event_level
        self.event_description = event_description
        self.event_status = 'new'
        