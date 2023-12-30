from traffic_manager import TrafficMng


def illegalOccupationDetect(msg: list, traffic: TrafficMng, config: dict):
    '''function illegalOccupationDetect

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

    检测非法占用应急车道事件, 输出并返回事件列表
    '''
    events_o = []

    return events_o
