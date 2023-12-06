def recieve(msg):
    '''
    接受传来的数据message, 将原始数据格式转化为代码内流通的数据格式。
    input
    ------
    msg: list, 传感器数据.
    msg元素为代表一个车辆目标的dict
    
    func
    ------
    1. 为每个target目标增加加速度属性a
    '''
    for i in range(len(msg)):
        msg[i]['a'] = 0
    return msg