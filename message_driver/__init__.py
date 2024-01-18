# 数据格式接口, 从接收数据转化为内部处理数据
interface = {'TargetId': 'id',
             'XDecx': 'x',
             'YDecy': 'y',
             'VDecVx': 'vx',
             'VDecVy': 'vy',
             'Xsize': 'width',
             'Ysize': 'length',
             'TargetType': 'class',
             'LineNum': 'laneID'
             }
# 返还数据格式接口, 从内部处理数据转化为输出数据
interface_back = dict()
for key in interface.keys():
    interface_back[interface[key]] = key


class Driver():
    '''class Driver

    数据格式转化驱动器，将传感器数据转化为代码内部流通的数据格式，
    将代码内部流通的数据格式转化为输出数据。
    '''
    def receive(self, msg: list) -> (bool, list):
        '''function receive

        input
        ------
        msg: list, 传感器数据。msg元素为代表一个车辆目标的dict。

        reutrn
        ------
        msg: list, 代码内流通的数据格式。

        接受传来的数据message, 将原始数据格式转化为代码内流通的数据格式。
        具体为: 修改原始数据属性名称为代码内部流通数据的属性名称。
        '''
        # 检查传输信息是否为目标数据
        valid = self._ifValid(msg)
        if not valid:
            return False, msg
        for i in range(len(msg)):
            # 修改属性名称
            for key in interface.keys():
                msg[i][interface[key]] = msg[i][key]
                del msg[i][key]
            # TODO 暂时在driver中加入，应当放在prepro中
            msg[i]['a'] = 0
            msg[i]['speed'] = (msg[i]['vx']**2 + msg[i]['vy']**2)**0.5
            msg[i]['laneNeedAdd'] = False
            if msg[i]['laneID'] > 100:
                msg[i]['laneID'] -= 100
                msg[i]['laneNeedAdd'] = True
        return True, msg

    def send(self, msg: list) -> list:
        '''function send

        input
        ------
        msg: list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。

        return
        ------
        msg: list, 输出到外部的数据。

        将代码内部流通的数据, 转化为输出需要的格式。返回值与代码内流通相比相比:
        具体为: 还原代码内部流通数据为原始数据属性名称的属性名称,
        并删除内部增加的属性。
        '''
        for i in range(len(msg)):
            # 还原属性名称
            for key in interface_back.keys():
                msg[i][interface_back[key]] = msg[i][key]
                del msg[i][key]
            # TODO 除del外的操作, 暂时在driver中加入, 应当放在prepro中
            del msg[i]['a']
            del msg[i]['speed']
            if msg[i]['laneNeedAdd']:
                msg[i][interface_back['laneID']] += 100
                del msg[i]['laneNeedAdd']

        return msg

    def _ifValid(self, msg) -> bool:
        '''function _ifValid

        input
        -----
        msg: list | str
            传感器数据, list | str格式。list为传感器数据, str为传输信息。

        return
        ------
        bool

        判断数据是否有效, 若为str信息则返回False。
        '''
        return type(msg) == list
