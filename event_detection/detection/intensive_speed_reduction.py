
def intensiveSpeedReductionDetect(msg, traffic, config, clb):
    '''function intensiveSpeedReductionDetect
    
    input
    ------
    msg: list, 传感器数据
    traffic: dict, 交通流数据
    config: dict, 标定参数
    self.clb: dict, 算法参数

    output
    ------
    events: list, 事件列表, 元素为event的衍生类

    检测急刹车事件, 输出并返回事件列表。减速判断也需要考虑加速度a方向需要跟v方向相反。
    '''
    events_r = []

    return events_r