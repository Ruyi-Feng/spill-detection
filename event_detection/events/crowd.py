from traffic_manager import TrafficMng


def crowdDetect(traffic: TrafficMng, dstc: float, vc: float):
    '''function crowdDetect

    input
    ------
    traffic:
        dict, 交通流数据
    dstc:
        float, density_crowd, 拥堵密度阈值, 单位辆/km
    vc:
        float, v_crowd, 拥堵速度阈值, 单位m/s

    output
    ------
    events: list, 事件列表, 元素为event的衍生类

    检测拥堵事件，输出并返回事件列表
    '''
    events_c = []

    return events_c
