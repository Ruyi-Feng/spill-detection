class Driver():
    '''class Driver

    数据格式转化驱动器，将传感器数据转化为代码内部流通的数据格式，将代码内部流通的数据格式转化为输出数据。
    '''
    def receive(self, msg: list) -> list:
        '''function receive
        
        input
        ------
        msg: list, 传感器数据。msg元素为代表一个车辆目标的dict。
        
        reutrn
        ------
        msg: list, 代码内流通的数据格式。

        接受传来的数据message, 将原始数据格式转化为代码内流通的数据格式。返回值与接受的msg相比: 
        1. 增加加速度属性a
        2. 增加速度属性speed, 单位m/s
        '''
        for i in range(len(msg)):
            msg[i]['a'] = 0
            msg[i]['speed'] = 0
            msg[i]['cell'] = {'lane': -1, 'order': -1}
        return msg

    def send(self, msg: list) -> list:
        '''function send
        
        input
        ------
        msg: list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。
        
        return
        ------
        msg: list, 输出到外部的数据。

        将代码内部流通的数据, 转化为输出需要的格式。返回值与代码内流通相比相比: 
        1. 删除加速度属性a
        2. 删除速度属性speed
        '''
        for i in range(len(msg)):
            del msg[i]['a']
            del msg[i]['speed']
            del msg[i]['cell']
        return msg
