
def intensive_speed_reduction_detect(msg, traffic, config, param):
    '''
    检测拥堵事件，输出并返回事件列表
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    param: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类
    '''
    events_r = []

    return events_r