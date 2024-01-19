from utils import int2strID
from traffic_manager.lane_manager import LaneMng
from traffic_manager.cell_manager import CellMng

'''This is to define the event class and event manager class.'''


class EventMng():
    '''class EventMng

    按一定架构管理事件

    properties
    ----------
    events: dict, 按字典组织的事件

    methods
    -------
    run: 执行事件管理, 将事件信息添加到events中
    clear: 清空events, 在每帧结束后调用, 以清空

    事件events格式
    events = {'spill': {'name': 'spill', 'occured': False,
                        'items': {eventID1: event1,
                                    eventID2: event2,
                                    ...}}
              'stop': {'name': 'stop', 'occured': False,
                         'items': {eventID1: event1,
                                   eventID2: event2,
                                   ...}}
            ...}
    '''
    def __init__(self, eventTypes: list):
        '''function __init__

        初始化事件管理器
        '''
        # encode event types
        num = len(eventTypes)
        self.eventTypes = eventTypes
        self.typeIdDict = {self.eventTypes[i]: i for i in range(num)}   # 数字编码
        self.typeCharDict = ({chr(i+65): i for i in range(num)})    # A起始字母编码
        # formulate event format
        self.eventsFormat = dict()
        for type in self.eventTypes:
            self.eventsFormat[type] = {'name': type, 'occured': False,
                                       'items': dict()}
        self.events = self.eventsFormat.copy()
        # initialize event ID
        self.eventIdCount = {char: 0 for char in self.typeCharDict}  # 每类最多百万

    def run(self, type: str, time: str, *originalInfo: any):
        '''function run

        input
        -----
        type: str, 事件类型
        time: str, 事件发生时间
        originalInfo: any, 事件信息, 为可变数量的参数。
        - 当type为'spill'时, originalInfo为[cellMng]
        - 当type为'stop', 'lowSpeed', 'highSpeed', 'EmergencyBrake',
          'illegalOccupation'时, originalInfo为[car]
        - 当type为'incident'时, originalInfo为[car1, car2]
        - 当type为'crowd'时, originalInfo为[laneMng]

        执行事件管理, 将事件信息添加到events中。在检测到event时调用。
        '''
        # distribute event ID
        eventID = self.typeCharDict[type] + int2strID(self.eventIdCount[type])
        self.eventIdCount[type] += 1
        self.eventIdCount[type] %= 10000000
        # formulate event info
        event = self._generateEvent(type, eventID, time, originalInfo)
        # add event to events
        self.events[type]['occured'] = True
        self.events[type]['items'][eventID] = event

    def clear(self):
        '''function clear
        
        清空events, 在每帧事件检测结束后调用, 即ed.run()末尾。
        '''
        self.events = self.eventsFormat.copy()

    def _generateEvent(self, type: str, eventID: str, time: str, *originalInfo: any):
        '''function _generateEvent

        生成事件实例, 用于添加到events中
        '''
        if type == 'spill':
            event = SpillEvent(time, eventID, originalInfo[0])
        elif type in ['stop', 'lowSpeed', 'highSpeed',
                      'emergencyBrake', 'illegalOccupation']:
            event = SingleCarEvent(time, originalInfo[0])
        elif type == 'incident':
            event = IncidentEvent(time, originalInfo[0], originalInfo[1])
        elif type == 'crowd':
            event = CrowdEvent(time, originalInfo[0])
        else:
            raise ValueError(f"Invalid event type '{type}' is defined.")
        return event


class BaseEvent():
    '''class BaseEvent

    事件类, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    time: str, 事件发生时间

    methods
    -------
    __init__: 初始化事件
    '''
    def __init__(self, type: str, eventID: str, time: str):
        '''function __init__

        初始化事件
        '''
        self.type = type
        self.eventID = eventID
        self.time = time


class SpillEvent(BaseEvent):
    '''class SpillEvent

    抛洒物事件类, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    time: float, 事件发生时间
    laneID: str, 事件发生的laneID
    order: int, 事件发生的lane的顺序
    start: float, 事件发生的lane的起点
    end: float, 事件发生的lane的终点
    danger: float, 事件发生的lane的危险系数
    '''
    def __init__(self, type: str, eventID: str, time: str, cell: CellMng):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        time: str, 事件发生时间
        cell: CellMng, 事件发生的cell
        '''
        super().__init__(type, eventID, time)
        self.laneID = cell.laneID
        self.order = cell.order
        start, end = cell.start, cell.end
        if start > end:
            start, end = end, start
        self.start = start
        self.end = end
        self.danger = cell.danger


class SingleCarEvent(BaseEvent):
    '''class SingleCarEvent
    
    单车事件类, 包括静止, 低速, 高速, 紧急制动, 违章占道, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    time: float, 事件发生时间
    carID: str, 事件发生的车辆ID
    laneID: str, 事件发生的车道ID
    x, y: float, 事件发生的车辆位置
    vx, vy: float, 事件发生的车辆速度
    speed: float, 事件发生的车辆速度
    a: float, 事件发生的车辆加速度
    '''
    def __init__(self, type: str, eventID: str, time: str, car: dict):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        time: str, 事件发生时间
        car: dict, 事件发生的车辆信息
        '''
        super().__init__(type, eventID, time)
        self.carID = car['id']
        self.laneID = car['laneID']
        self.x, self.y = car['x'], car['y']
        self.vx, self.vy = car['vx'], car['vy']
        self.speed = car['speed']
        self.a = car['a']


class IncidentEvent(BaseEvent):
    '''class IncidentEvent

    事故事件类, 以class形式存储事件信息

    properties
    ----------
    time: float, 事件发生时间
    carID1, carID2: str, 事件发生的车辆ID
    laneID1, laneID2: str, 事件发生的车道ID
    x1, y1, x2, y2: float, 事件发生的车辆位置
    vx1, vy1, vx2, vy2: float, 事件发生的车辆速度
    speed1, speed2: float, 事件发生的车辆速度
    a1, a2: float, 事件发生的车辆加速度
    '''
    def __init__(self, type: str, eventID: str, time: str,
                 car1: dict, car2: dict):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        time: str, 事件发生时间
        car1: dict, 事件发生的车辆信息
        car2: dict, 事件发生的车辆信息
        '''
        super().__init__(type, eventID, time)
        self.carID1 = car1['id']
        self.carID2 = car2['id']
        self.laneID1 = car1['laneID']
        self.laneID2 = car2['laneID']
        self.x1, self.y1 = car1['x'], car1['y']
        self.x2, self.y2 = car2['x'], car2['y']
        self.vx1, self.vy1 = car1['vx'], car1['vy']
        self.vx2, self.vy2 = car2['vx'], car2['vy']
        self.speed1 = car1['speed']
        self.speed2 = car2['speed']
        self.a1 = car1['a']
        self.a2 = car2['a']


class CrowdEvent(BaseEvent):
    '''class CrowdEvent

    拥堵事件类, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    time: float, 事件发生时间
    laneID: str, 事件发生的laneID
    q: float, 事件发生的lane的q
    k: float, 事件发生的lane的k
    v: float, 事件发生的lane的v
    '''
    def __init__(self, type: str, eventID: str, time: str, lane: LaneMng):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        time: str, 事件发生时间
        lane: LaneMng, 事件发生的lane
        '''
        super().__init__(type, eventID, time)
        self.laneID = lane.laneID
        self.q = lane.q
        self.k = lane.k
        self.v = lane.v
