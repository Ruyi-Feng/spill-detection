from traffic_manager import TrafficMng


def incidentDetect(msg: list, traffic: TrafficMng, config: dict):
    '''function incidentDetect

    input
    ------
    msg:
        list, 传感器数据
    traffic:
        TrafficMng, 交通管理器, 存有交通流信息
    config:
        dict, 标定参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类

    检测多车事故事件, 输出并返回事件列表
    '''
    events_i = []

    return events_i
