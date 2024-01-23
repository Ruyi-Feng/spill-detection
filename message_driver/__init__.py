'''Define the send and receive interface processor of message.'''


# 数据格式接口, 从接收数据转化为内部处理数据
# TODO 根据实际接收数据情况修改
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

# 从内部数据输出到外部应删除的键值
keys2delete = ['laneNeedAdd', 'speed', 'a', 'ax', 'ay', 'timeStamp', 'secMark']

# count记录最大值(达到后重置)ss
maxCount = 60000
# maxCount = 172800000    # fps=20时, 10天重置1次


class Driver():
    '''class Driver

    数据格式转化驱动器, 将传感器数据转化为代码内部流通的数据格式,
    将代码内部流通的数据格式转化为输出数据。
    '''
    def __init__(self):
        self.count = 0

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
        # 转化数据格式
        for i in range(len(msg)):
            self._formatTransOuter2Inner(msg[i])
        # 更新时间戳count
        self.count += 1
        self.count %= maxCount
        return True, msg

    def send(self, cars: list, events: dict) -> (list, list):
        '''function send

        input
        ------
        cars: list, 代码内流通的数据格式。msg元素为代表一个车辆目标的dict。
        events: dict, 代码内部的事件信息。

        return
        ------
        msg: list, 输出到外部的数据。
        events: dict, 向外传输格式的事件信息。

        将代码内部流通的数据, 转化为输出需要的格式。返回值与代码内流通相比相比:
        具体为: 还原代码内部流通数据为原始数据属性名称的属性名称,
        并删除内部增加的属性。
        将事件信息转化为输出需要的格式。
        '''
        # 数据格式转化
        msg = []
        for i in range(len(cars)):
            newCar = self._formatTransInner2Outer(cars[i])
            msg.append(newCar)
        # 事件格式转化
        outEvents = self._eventsInner2Outer(events)
        return msg, outEvents

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

    def _formatTransOuter2Inner(self, car: dict):
        '''function _formatTransOuter2Inner

        input
        -----
        car: dict, 传感器的单车数据, dict格式。

        将msg中car的数据格式转化为代码内部的处理数据格式。
        原地修改
        '''
        # 调整属性名称
        for key in interface.keys():
            car[interface[key]] = car[key]
            del car[key]
        # 处理特殊属性
        car['speed'] = (car['vx']**2 + car['vy']**2)**0.5
        car['laneNeedAdd'] = False
        if car['laneID'] > 100:
            car['laneID'] -= 100
            car['laneNeedAdd'] = True
        # 调整时间戳格式
        # TODO 暂时在接收数据时按照接收count为数据赋值时间戳
        # TODO 后续根据具体情况, 将时间戳转化为以毫秒ms为单位的时间戳
        # 可以转化成unix时间戳(统一确定了一个时间原点), 再将这个s为单位的数据转化为ms为单位
        # 统一将时间戳记为以毫秒ms为单位
        car['timeStamp'] = self.count * 100
        car['secMark'] = car['timeStamp'] % maxCount           # 用于complete使用

    def _formatTransInner2Outer(self, car: dict) -> dict:
        '''function _formatTransInner2Outer

        input
        -----
        car: dict, 代码内部的处理数据格式, dict格式。

        将代码内部处理的car数据形式, 返还成msg中传输来的原始格式。
        原地修改
        '''
        newCar = car.copy()
        # 处理特殊属性
        if newCar['laneNeedAdd']:
            newCar['laneID'] += 100
        # 调整属性名称
        for key in interface_back.keys():
            newCar[interface_back[key]] = newCar[key]
            del newCar[key]
        # TODO 注意要保留原始的时间戳
        for k in keys2delete:
            if k in newCar.keys():
                del newCar[k]

        return newCar

    def _eventsInner2Outer(self, events: dict) -> list:
        '''function _eventsInner2Outer

        input
        -----
        events: dict, 代码内部的事件信息, dict格式。

        将代码内部的事件信息转化为传输格式的事件信息。
        '''
        outerEvents = []
        for type in events.keys():
            if not events[type]['occured']:
                continue
            for eventID in events[type]['items']:
                outerEvents.append(events[type]['items'][eventID])
        return outerEvents
