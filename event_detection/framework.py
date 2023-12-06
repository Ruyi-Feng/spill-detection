from algo_lib import *
default_event_types = ['crowd', 'high_speed', 'illegal_occupation', 'incident_single_car', 
                      'incident', 'intensive_speed_reduction', 'low_speed', 'spill']


def event_detection(msg, traffic, config, param, event_types = default_event_types):
    '''
    检测交通事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    param: dict, 算法参数
    event_types: list, 需要检测的事件列表。

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    # 事件检测
    events = []
    if 'crowd' in event_types:
        events_c = crowd_detect(msg, traffic, config, param)
        events += events_c
    if 'high_speed' in event_types:
        events_h = high_speed_detect(msg, traffic, config, param)
        events += events_h
    if 'illegal_occupation' in event_types:
        events_o = illegal_occupation_detect(msg, traffic, config, param)
        events += events_o
    if 'incident_single_car' in event_types:
        events_is = incident_single_car_detect(msg, traffic, config, param)
        events += events_is
    if 'incident' in event_types:
        events_i = incident_detect(msg, traffic, config, param)
        events += events_i
    if 'intensive_speed_reduction' in event_types:
        events_r = intensive_speed_reduction_detect(msg, traffic, config, param)
        events += events_r
    if 'low_speed' in event_types:
        events_l = low_speed_detect(msg, traffic, config, param)
        events += events_l
    if 'spill' in event_types:
        events_s = spill_detect(msg, traffic, config, param)
        events += events_s
    
    return events

    