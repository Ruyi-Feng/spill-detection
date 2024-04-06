from datetime import datetime
from copy import deepcopy
from utils import int2strID
from traffic_manager.lane_manager import LaneMng
from traffic_manager.cell_manager import CellMng
from utils.default import defaultEventTypes, typeCharDict, typeIdDict
from .event_filter import EventFilter


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
                        'items': {eventID1: event1--dtct,
                                  eventID2: event2--dtct,
                                  ...}}
              'stop': {'name': 'stop', 'occured': False,
                         'items': {eventID1: event1--dtct,
                                   eventID2: event2--dtct,
                                   ...}}
            ...}
    '''
    def __init__(self):
        '''function __init__

        初始化事件管理器
        '''
        # encode event types
        self.eventTypes = defaultEventTypes
        self.typeIdDict = typeIdDict
        self.typeCharDict = typeCharDict
        # formulate event format
        self.eventsFormat = dict()
        for type in self.eventTypes:
            self.eventsFormat[type] = {'name': type, 'occured': False,
                                       'items': dict()}
        self.events = self.eventsFormat.copy()
        # initialize event ID, 规则: 日期+五位计数器
        self.eventIdCount = {type: 0 for type in defaultEventTypes}
        self.currentDay = datetime.now().strftime('%Y%m%d')
        self.idLen = 5
        # 事件过滤器, 用于防止同id长期多次报警
        self.ef = EventFilter()

    def run(self, type: str, startTime: int, endTime: int,
            *info: any):
        '''function run

        input
        -----
        type: str, 事件类型
        startTime: int, 事件发生unix时间戳, 单位ms
        endTime: int, 事件结束unix时间戳, 单位ms
        info: any, 事件信息, 为可变数量的参数。
        - 当type为'spill'时, info为[cellMng, deviceID, deviceType, eventID,
          'start'/'end']
        - 当type为'stop', 'lowSpeed', 'highSpeed', 'EmgcBrake',
          'illegalOccupation'时, info为[car, eventID, 'start'/'end']
        - 当type为'incident'时, info为[car1, car2]
        - 当type为'crowd'时, info为[laneMng, deviceID, deviceType, eventID,
          'start'/'end']

        执行事件管理, 将事件信息添加到events中。在检测到event时调用。
        '''
        # 重置计数
        if self.currentDay != datetime.now().strftime('%Y%m%d'):
            self.eventIdCount = {type: 0 for type in defaultEventTypes}
            self.currentDay = datetime.now().strftime('%Y%m%d')
        # 过滤已经报警的数据(3分钟缓存内记录的id和type不会再报警)
        ifFilter = self.ef.run(type, startTime, endTime, info)
        if ifFilter:    # 如果过滤, 将不会分配eventID, 不会生成事件
            return None
        # distribute event ID
        # 为新事件
        if (
            ((type in ['stop', 'lowSpeed', 'highSpeed',
                       'illegalOccupation', 'emgcBrake'])
                       and (info[1] == '')) or
            ((type in ['spill', 'crowd']) and (info[3] == '')) or
            (type == 'incident')
        ):
            self.eventIdCount[type] += 1
            eventID = self.currentDay + '-' + typeCharDict[type] +\
                int2strID(self.eventIdCount[type], self.idLen)
        else:  # 从已经记录的id继承
            if (type in ['stop', 'lowSpeed', 'highSpeed',
                       'illegalOccupation', 'emgcBrake']):
                eventID = info[1]
            elif type in ['spill', 'crowd']:
                eventID = info[3]

        # formulate event
        event = self._generateEvent(type, eventID, startTime, endTime, info)
        # add event to events
        self.events[type]['occured'] = True
        self.events[type]['items'][eventID] = vars(event)
        return eventID

    def clear(self):
        '''function clear

        清空events, 在每帧事件检测结束后调用, 即ed.run()末尾。
        '''
        self.events = deepcopy(self.eventsFormat)

    def _generateEvent(self, type: str, eventID: str,
                       startTime: int, endTime: int, info: any):
        '''function _generateEvent

        生成事件实例, 用于添加到events中
        '''
        # startTime和endTime转化为年月日时分秒格式

        if type == 'spill':
            event = SpillEvent(type, eventID, startTime, endTime,
                               info[0], info[1], info[2])
        elif type in ['stop', 'lowSpeed', 'highSpeed',
                      'emgcBrake', 'illegalOccupation']:
            event = SingleCarEvent(type, eventID, startTime, endTime, info[0])
        elif type == 'incident':
            event = IncidentEvent(type, eventID, startTime, endTime,
                                  info[0], info[1])
        elif type == 'crowd':
            event = CrowdEvent(type, eventID, startTime, endTime,
                               info[0], info[1], info[2])
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
    startTime: str, 事件发生时间
    endTime: str, 事件结束时间

    methods
    -------
    __init__: 初始化事件
    '''
    def __init__(self, type: str, eventID: str, startTime: str, endTime: str):
        '''function __init__

        初始化事件
        '''
        self.type = type
        self.eventID = eventID
        self.startTime = startTime
        self.endTime = endTime


class SpillEvent(BaseEvent):
    '''class SpillEvent

    抛洒物事件类, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    startTime: str, 事件发生时间
    endTime: str, 事件结束时间
    laneID: str, 事件发生的laneID
    order: int, 事件发生的lane的顺序
    start: float, 事件发生的lane的起点
    end: float, 事件发生的lane的终点
    danger: float, 事件发生的lane的危险系数
    lat: int, 事件发生的元胞的order
    lon: int, 事件发生的元胞的start
    rawClass: int, 事件车辆的种类, 无车为-1
    '''
    def __init__(self, type: str, eventID: str,
                 startTime: str, endTime: str,
                 cell: CellMng,
                 deviceID: str, deviceType: str):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        startTime: str, 事件发生时间
        endTime: str, 事件结束时间
        cell: CellMng, 事件发生的cell
        deviceID: str, 事件发生的设备ID
        deviceType: str, 事件发生的设备类型
        '''
        super().__init__(type, eventID, startTime, endTime)
        self.laneID = cell.laneID
        self.order = cell.order
        start, end = cell.start, cell.end
        if start > end:
            start, end = end, start
        self.start = start
        self.end = end
        self.danger = cell.danger
        self.lat = self.order      # for compatibility
        self.lon = cell.start      # for compatibility
        self.deviceID = deviceID
        self.deviceType = deviceType
        self.rawClass = -1


class SingleCarEvent(BaseEvent):
    '''class SingleCarEvent

    单车事件类, 包括静止, 低速, 高速, 紧急制动, 违章占道, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    startTime: str, 事件发生时间
    endTime: str, 事件结束时间
    carID: str, 事件发生的车辆ID
    laneID: str, 事件发生的车道ID
    x, y: float, 事件发生的车辆位置
    vx, vy: float, 事件发生的车辆速度
    speed: float, 事件发生的车辆速度
    a: float, 事件发生的车辆加速度
    lat: float, 事件发生的车辆纬度
    lon: float, 事件发生的车辆经度
    deviceID: str, 事件发生的设备ID
    deviceType: str, 事件发生的设备类型
    rawClass: int, 事件车辆的种类, 无车为-1
    '''
    def __init__(self, type: str, eventID: str,
                 startTime: str, endTime: str,
                 car: dict):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        startTime: str, 事件发生时间
        endTime: str, 事件结束时间
        car: dict, 事件发生的车辆信息
        '''
        super().__init__(type, eventID, startTime, endTime)
        self.carID = car['id']
        self.laneID = car['laneID']
        self.x, self.y = car['x'], car['y']
        self.vx, self.vy = car['vx'], car['vy']
        self.speed = car['speed']
        self.a = car['a']
        self.lat = car['latitude']
        self.lon = car['longitude']
        self.deviceID = car['deviceID']
        self.deviceType = car['deviceType']
        self.rawClass = car['class']


class IncidentEvent(BaseEvent):
    '''class IncidentEvent

    事故事件类, 以class形式存储事件信息

    properties
    ----------
    startTime: str, 事件发生时间
    endTime: str, 事件结束时间
    carID1, carID2: str, 事件发生的车辆ID
    laneID1, laneID2: str, 事件发生的车道ID
    x1, y1, x2, y2: float, 事件发生的车辆位置
    vx1, vy1, vx2, vy2: float, 事件发生的车辆速度
    speed1, speed2: float, 事件发生的车辆速度
    a1, a2: float, 事件发生的车辆加速度
    lat, lon: float, 事件发生的车辆经纬度
    deviceID: str, 事件发生的设备ID
    deviceType: str, 事件发生的设备类型
    rawClass: int, 事件车辆的种类, 无车为-1, 肇事为list
    '''
    def __init__(self, type: str, eventID: str,
                 startTime: str, endTime: str,
                 car1: dict, car2: dict):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        startTime: str, 事件发生时间
        endTime: str, 事件结束时间
        car1: dict, 事件发生的车辆信息
        car2: dict, 事件发生的车辆信息
        '''
        super().__init__(type, eventID, startTime, endTime)
        self.carID1 = car1['id']
        self.carID2 = car2['id']
        self.laneID = car1['laneID']  # 撞车的两车位置应当一样
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
        self.lat = car1['latitude']     # 撞车的两车位置应当一样
        self.lon = car1['longitude']
        self.deviceID = car1['deviceID']
        self.deviceType = car1['deviceType']
        self.rawClass = [car1['class'], car2['class']]


class CrowdEvent(BaseEvent):
    '''class CrowdEvent

    拥堵事件类, 以class形式存储事件信息

    properties
    ----------
    type: str, 事件类型
    eventID: str, 事件ID
    startTime: str, 事件发生时间
    endTime: str, 事件结束时间
    laneID: str, 事件发生的laneID
    q: float, 事件发生的lane的q
    k: float, 事件发生的lane的k
    v: float, 事件发生的lane的v
    lat: int, 事件发生的lane的ID
    lon: float, 事件发生的lane的q
    deviceID: str, 事件发生的设备ID
    deviceType: str, 事件发生的设备类型
    rawClass: int, 事件车辆的种类, 无车为-1
    '''
    def __init__(self, type: str, eventID: str,
                 startTime: str, endTime: str,
                 lane: LaneMng,
                 deviceID: str, deviceType: str):
        '''function __init__

        input
        -----
        type: str, 事件类型
        eventID: str, 事件ID
        startTime: str, 事件发生时间
        endTime: str, 事件结束时间
        lane: LaneMng, 事件发生的lane
        '''
        super().__init__(type, eventID, startTime, endTime)
        self.laneID = lane.ID
        self.q = lane.q
        self.k = lane.k
        self.v = lane.v
        self.lat = lane.ID  # for compatibility
        self.lon = lane.q   # for compatibility
        self.deviceID = deviceID
        self.deviceType = deviceType
        self.rawClass = -1
