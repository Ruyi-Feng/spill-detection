def send(msg):
    '''
    将代码内部流通的数据, 转化为输出需要的格式。
    input
    ------
    msg: list, 内部流通数据.
    msg元素为代表一个车辆目标的dict
    
    func
    ------
    1. 为每个target目标删除加速度属性a
    '''
    for i in range(len(msg)):
        del msg[i]['a']
    return msg
