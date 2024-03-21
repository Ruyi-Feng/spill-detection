from logger import MyLogger
from utils.default import typeIdDict
from utils import unixMilliseconds2Datetime

'''Define the send and receive interface processor of message.'''


# count记录最大值(达到后重置)ss
maxCount = 60000            # 1min对应的最大ms时长
# maxCount = 172800000    # fps=20时, 10天重置1次


class Driver():
    '''class Driver

    数据格式转化驱动器, 将传感器数据转化为代码内部流通的数据格式,
    将代码内部流通的数据格式转化为输出数据。
    '''
    def __init__(self, fps: float, logger: MyLogger = None):
        self.fps = fps
        self.logger = logger if logger else MyLogger('Driver', 'notDefined')
        self.driverOffline = DriverOffline(fps, logger)
        self.driverOnline = DriverOnline(fps, logger)
        self.mode = 'offline'   # 'offline' | 'online', 默认为离线测试模式, receive时更新

    def setLanes(self, lanes: list) -> None:
        '''function setLanes

        input
        -----
        lanes: list, 道路的车道号列表。

        更新车道号列表。将用于检查输入的目标车辆lane是否在标定的车道列表中,
        若出现不在列表中的车道号, 则报警, 应当用更长的时间进行标定。
        '''
        self.driverOnline.lanes = lanes

    def receive(self, msg) -> (bool, list):
        '''function receive

        input
        ------
        msg: list | dict |str, 传感器数据。
        list为离线数据, dict为在线数据, str为传输信息。

        reutrn
        ------
        bool, 判断数据是否有效, 若为str信息则返回False。
        msg: list, 代码内流通的数据格式。

        接受传来的数据message, 将原始数据格式转化为代码内流通的数据格式。
        '''
        if not (self._validMsg(msg)):
            return False, msg
        if type(msg) == dict:
            # 在线部署情况
            self.mode = 'online'
            return True, self.driverOnline.recieve(msg)
        elif type(msg) == list:
            # 离线测试情况
            self.mode = 'offline'
            return True, self.driverOffline.recieve(msg)

    def _validMsg(self, msg) -> bool:
        '''function _validMsg

        input
        -----
        msg: list | dict |str, 传感器数据。
        list为离线数据, dict为在线数据, str为传输信息。

        return
        ------
        bool, 判断数据是否有效, 若为str信息,
        或者为dict时'targets'长度为0,
        或者list时长度为0, 则返回False。
        '''
        if (type(msg) == str):
            return False
        elif type(msg) == dict:
            if len(msg['targets']) == 0:
                return False
        elif type(msg) == list:
            if len(msg) == 0:
                return False
        return True

    def send(self, cars: list, events: dict) -> (list, list):
        '''function send
        input
        ------
        events: dict, 代码内部的事件信息。

        return
        ------
        events: dict, 向外传输格式的事件信息。

        将代码内部流通的数据, 转化为输出需要的格式。返回值与代码内流通相比相比:
        具体为: 还原代码内部流通数据为原始数据属性名称的属性名称,
        并删除内部增加的属性。
        将事件信息转化为输出需要的格式。
        '''
        if self.mode == 'online':
            return self.driverOnline.send(cars, events)
        elif self.mode == 'offline':
            return self.driverOffline.send(cars, events)


class DriverOffline:
    '''class DriverOffline

    离线测试驱动器, 用于离线测试时的数据接收与发送。
    '''
    def __init__(self, fps, logger) -> None:
        self.fps = fps
        self.logger = logger
        self.count = 0                          # 用于开发阶段测试, 不用于实际部署
        self.timeIntervalMs = int(1000 / fps)   # 用于开发阶段测试, 不用于实际部署
        # 数据格式接口, 从接收数据转化为内部处理数据
        interface = {'TargetId': 'id',
                     'XDecx': 'x',
                     'YDecy': 'y',
                     'VDecVx': 'vx',
                     'VDecVy': 'vy',
                     'Xsize': 'width',
                     'Ysize': 'length',
                     'TargetType': 'class',
                     'LineNum': 'laneID',
                     'Latitude': 'latitude',
                     'Longitude': 'longitude',
                     'TargetType': 'class'
                     }
        # 返还数据格式接口, 从内部处理数据转化为输出数据
        interfaceBack = dict()
        for key in interface.keys():
            interfaceBack[interface[key]] = key
        # 从内部数据输出到外部应删除的键值
        keys2delete = ['laneNeedAdd', 'speed', 'a', 'ax', 'ay',
                       'timestamp', 'secMark', 'deviceID', 'deviceType']
        self.interface = interface
        self.interfaceBack = interfaceBack
        self.keys2delete = keys2delete

    def recieve(self, msg: list) -> list:
        '''function recieve

        input
        -----
        msg: list, 传感器数据。msg元素为代表一个车辆目标的dict。

        return
        ------
        msg: list, 代码内流通的数据格式。

        接受传来的数据message, 将原始数据格式转化为代码内流通的数据格式。
        具体为: 修改原始数据属性名称为代码内部流通数据的属性名称。
        '''
        # 转化数据格式
        for i in range(len(msg)):
            self._formatTransOuter2Inner(msg[i])
        # 更新时间戳count
        self.count += 1
        self.count %= maxCount  # 这里就借用一下maxCount, 不用考虑数值意义, 多少都行, 达一定值后重置避免溢出
        return msg

    def send(self, cars: list, events: dict) -> (list, list):
        '''function send
        input
        ------
        events: dict, 代码内部的事件信息。

        return
        ------
        events: list, 向外传输格式的事件信息。

        将代码内部流通的数据, 转化为输出需要的格式。返回值与代码内流通相比相比:
        具体为: 还原代码内部流通数据为原始数据属性名称的属性名称,
        并删除内部增加的属性。
        将事件信息转化为输出需要的格式。
        '''
        # 若需输出目标数据, 在这里重新组织, 调用_formatTransInner2Outer()修改属性
        # 目前若重新组织目标数据，会导致在预处理的补全阶段因数据引用出现报错
        # for car in cars:
        #     self._formatTransInner2Outer(car)
        # 事件格式转化
        outEvents = self._eventsInner2Outer(events)
        return cars, outEvents

    def _formatTransOuter2Inner(self, car: dict):
        '''function _formatTransOuter2Inner

        input
        -----
        car: dict, 传感器的单车数据, dict格式。

        将msg中car的数据格式转化为代码内部的处理数据格式。
        原地修改
        '''
        # 调整属性名称
        for key in self.interface.keys():
            car[self.interface[key]] = car[key]
            del car[key]
        # 处理特殊属性
        car['speed'] = (car['vx']**2 + car['vy']**2)**0.5
        car['laneNeedAdd'] = False
        if car['laneID'] > 100:
            car['laneID'] -= 100
            car['laneNeedAdd'] = True
        # 调整时间戳格式
        # 统一将时间戳记为ms的时间戳
        car['timestamp'] = self.count * self.timeIntervalMs
        car['secMark'] = car['timestamp'] % maxCount           # 用于complete使用
        # 补充在线数据有的属性
        car['deviceID'] = 'K68+366'
        car['deviceType'] = 1

    def _formatTransInner2Outer(self, car: dict) -> dict:
        '''function _formatTransInner2Outer

        input
        -----
        car: dict, 代码内部的处理数据格式, dict格式。

        将代码内部处理的car数据形式, 返还成msg中传输来的原始格式。
        原地修改
        '''
        # 处理特殊属性
        if car['laneNeedAdd']:
            car['laneID'] += 100
        # 调整属性名称
        for key in self.interfaceBack.keys():
            car[self.interfaceBack[key]] = car[key]
            del car[key]
        for k in self.keys2delete:
            if k in car.keys():
                del car[k]

    def _eventsInner2Outer(self, events: dict) -> list:
        '''function _eventsInner2OuterOffline

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


class DriverOnline:
    '''class DriverOnline

    在线部署驱动器, 用于在线部署时的数据接收与发送。
    '''
    def __init__(self, fps, logger) -> None:
        '''
        input
        -----
        fps: float, 数据帧率。
        lanes: list, 道路的车道号列表。
        '''
        self.fps = fps
        self.logger = logger
        # 数据格式接口, 从接收数据转化为内部处理数据
        interface = {
                    'cls': 'class',
                    'lane': 'laneID'
                    }
        # 返还数据格式接口, 从内部处理数据转化为输出数据
        interfaceBack = dict()
        for key in interface.keys():
            interfaceBack[interface[key]] = key
        # 从内部数据输出到外部应删除的键值
        keys2delete = ['laneNeedAdd', 'a', 'ax', 'ay', 'secMark']
        self.interface = interface
        self.interfaceBack = interfaceBack
        self.keys2delete = keys2delete
        self.lanes = list(range(20))    # 预设值，在启动controller检测时会根据标定结果设值

    def recieve(self, msg: dict) -> list:
        '''function recieve

        input
        -----
        msg: dict, 传感器数据。含键值:
        'deviceID': str, 'deviceType': str, 'targets': list.
        其中targets为list, 其元素为代表一个车辆目标的dict, 如:
        {
            "timestamp": 1705910562380,
            "id": 52,
            "lane": 2,
            "x": -93.31471856189998,
            "y": -1.4275749755241487,
            "latitude": 33.3333,
            "longitude": 111.1111,
            "cls": 0,
            "speed": 59.291003819294794,
            "vx": 1.0,
            "vy": 60.0
        }

        return
        ------
        msg: list, 代码内流通的数据格式。

        接受传来的数据message, 将原始数据格式转化为代码内流通的数据格式。
        具体为:
        将deviceID, deviceType, 都赋值给单个车辆目标dict。
        修改原始数据属性名称为代码内部流通数据的属性名称。
        '''
        deviceID = msg['deviceID']
        deviceType = msg['deviceType']
        cars = []
        for car in msg['targets']:
            self._formatTransOuter2Inner(car)
            # if car['laneID'] == 0:
            #     continue
            if car['laneID'] not in self.lanes:
                self.logger.warning('laneID '+ str(car['laneID'])+
                                    'not in lanes'+ str(self.lanes)+
                                    'please recalibrate the section: '+
                                    'deviceID:'+ deviceID+
                                    'deviceType:'+ str(deviceType))
                continue
            car['deviceID'] = deviceID
            car['deviceType'] = deviceType
            cars.append(car)
        return cars

    def send(self, cars: list, events: dict) -> (list, list):
        '''function send
        input
        ------
        events: dict, 代码内部的事件信息。

        return
        ------
        events: list, 向外传输格式的事件信息。

        将代码内部流通的数据, 转化为输出需要的格式。返回值与代码内流通相比相比:
        具体为: 还原代码内部流通数据为原始数据属性名称的属性名称,
        并删除内部增加的属性。
        将事件信息转化为输出需要的格式。
        '''
        # 若需输出目标数据, 在这里重新组织, 调用_formatTransInner2Outer()修改属性
        # 事件格式转化
        outEvents = self._eventsInner2Outer(events)
        return cars, outEvents

    def _formatTransOuter2Inner(self, car: dict):
        '''function _formatTransOuter2Inner

        input
        -----
        car: dict, 传感器的单车数据, dict格式。

        将msg中car的数据格式转化为代码内部的处理数据格式。
        原地修改
        '''
        # 调整属性名称
        for key in self.interface.keys():
            car[self.interface[key]] = car[key]
            del car[key]
        # 处理特殊属性
        car['laneNeedAdd'] = False
        if car['laneID'] > 100:
            car['laneID'] -= 100
            car['laneNeedAdd'] = True
        # 调整时间戳格式
        car['secMark'] = car['timestamp'] % maxCount    # 用于complete使用

    def _formatTransInner2Outer(self, car: dict):
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
        for key in self.interfaceBack.keys():
            newCar[self.interfaceBack[key]] = newCar[key]
            del newCar[key]
        for k in self.keys2delete:
            if k in newCar.keys():
                del newCar[k]

        return newCar

    def _eventsInner2Outer(self, events: dict) -> list:
        '''function _eventsInner2OuterOffline

        input
        -----
        events: dict, 代码内部的事件信息, dict格式。

        将代码内部的事件信息转化为传输格式的事件信息。
        转化后格式应为:
        {
            "type": 1,
            "level": 1,
            "start_time": "2023-12-06 11:11:11",
            "end_time": "2023-12-06 11:11:11",
            "lane": 1,
            "raw_class": 1,
            "point_wgs84": {
                "lat": 33.33,
                "lon": 111.11
            },
            "device_type": 1,
            "device_id": "K70+800"
        }
        '''
        outerEvents = []
        for type in events.keys():
            if not events[type]['occured']:
                continue
            for eventID in events[type]['items']:
                event = events[type]['items'][eventID]  # dict型
                event = self._eventInner2Outer(event)
                outerEvents.append(event)

        return outerEvents

    def _eventInner2Outer(self, event: dict) -> dict:
        '''function _eventInner2Outer

        input
        -----
        event: dict, 代码内部的事件信息, dict格式。

        修改event格式为协议中的格式。
        修改前:
        {
            'type': 'illegalOccupation',
            'eventID': 'H0000000',
            'startTime': 0,
            'endTime': -1,
            'carID': 5819,
            'laneID': 8,
            'x': 21.7,
            'y': 413.3,
            'vx': 0.06,
            'vy': 19.36,
            'speed': 19,
            'lat': 0,
            'lon': 0,
            'a': 0
        }
        修改后:
        {
            "type": 1,
            "level": 1,
            "start_time": "2023-12-06 11:11:11",
            "end_time": "2023-12-06 11:11:11",
            "lane": 1,
            "raw_class": 1,
            "point_wgs84": {
                "lat": 33.33,
                "lon": 111.11
            },
            "device_type": 1,
            "device_id": "K70+800"
        }
        '''
        newEvent = dict()
        # newEvent['type'] = typeIdDict[event['type']]
        # newEvent['level'] = 1
        # newEvent['start_time'] = unixMilliseconds2Datetime(event['startTime'])
        # if event['endTime'] == -1:
        #     newEvent['end_time'] = -1
        # else:
        #     newEvent['end_time'] = unixMilliseconds2Datetime(event['endTime'])
        # newEvent['lane'] = event['laneID']
        # newEvent['raw_class'] = event['rawClass']
        # newEvent['point_wgs84'] = {
        #     'lat': event['lat'],
        #     'lon': event['lon']
        # }
        # newEvent['device_type'] = event['deviceType']
        # newEvent['device_id'] = event['deviceID']
        # 上述用dict.update()的方式更新newEvent
        newEvent.update(
            {
                'type': typeIdDict[event['type']],
                'level': 1,
                'start_time': unixMilliseconds2Datetime(event['startTime']),
                'end_time': unixMilliseconds2Datetime(event['endTime']) \
                    if event['endTime'] != -1 else -1,
                'lane': event['laneID'],
                'raw_class': event['rawClass'],
                'point_wgs84': {'lat': event['lat'], 'lon': event['lon']},
                'device_type': event['deviceType'],
                'device_id': event['deviceID']
            })

        return newEvent
