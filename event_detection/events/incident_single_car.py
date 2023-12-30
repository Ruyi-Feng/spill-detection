from traffic_manager import TrafficMng


def incidentSingleCarDetect(msg: list, traffic: TrafficMng, config: dict):
    '''function incidentSingleCarDetect

    input
    ------
    msg:
        list, 传感器数据
    traffic:
        dict, 交通流数据
    config:
        dict, 标定参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类

    检测单车事故事件, 输出并返回事件列表
    '''
    events_is = []

    return events_is
