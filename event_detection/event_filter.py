from utils.default import defaultEventTypes


LIMITTIME = 3 * 60 * 1000   # 3分钟, ms单位, 若超过3分钟则重新报警


class EventFilter():
    '''class EventFilter

    编程便捷的角度对事件进行过滤, 
    当前会出现同一id的同一事件会多次报警的情况,
    限制在3分钟内事件开始和事件结束只报警一次。
    实现操作: 同一id同一type事件报警两次后, 开始限制3分钟。
    加入到pipeline的最后,driver之前。
    '''
    def __init__(self):
        '''
        缓存组织形式
        {
            'type': {
                'id': {
                    'start': false,
                    'end': false,
                    'time': int     # 时间戳, ms单位 
                }
            }
        }
        '''
        self.eventCache = {type: {} for type in defaultEventTypes}

    def run(self, type: str, startTime: int, endTime: int,
            *info: any) -> bool:
        '''function run

        input
        -----
        type: str, 事件类型
        startTime: int, 事件开始时间, ms单位
        endTime: int, 事件结束时间, ms单位
        info: any, 事件信息
        - 当type为'spill'时, info为[cellMng, deviceID, deviceType, eventID,
          'start'/'end']
        - 当type为'stop', 'lowSpeed', 'highSpeed', 'EmgcBrake',
          'illegalOccupation'时, info为[car, eventID, 'start'/'end']
        - 当type为'incident'时, info为[car1, car2]
        - 当type为'crowd'时, info为[laneMng, deviceID, deviceType, eventID,
          'start'/'end']

        return
        ------
        ifFilter: bool, 是否需要过滤

        返回该事件是否近期已经被报警, 如果已经报警, 则需要过滤返回True
        '''
        info = info[0]  # 传进来的时候会在外边又套一层tuple
        # 获取当前事件最新的时间戳
        timestamp = max(startTime, endTime)  # 可能endTime是-1
        # 获取列表索引
        key = self._getEventRecordKey(type, info)
        # 检查cache中是否有该id的该type事件
        self.eventCache[type].setdefault(key, {
            'start': False,
            'end': False,
            'time': timestamp
        })
        # 单独处理频繁报名的spill和crowd事件
        if type in ['spill', 'crowd'] and self._eventIsRealEnd4SpillAndCrowd(type, info):
            self.eventCache[type][key]['end'] = False   # 代表该事件真正结束, 不应被过滤
        beforeEnd = self.eventCache[type][key]['end']   # 之前是否已经结束
        # 更新时间戳
        self.eventCache[type][key]['time'] = timestamp
        # 根据事件类型与start/end标记更新对应字段
        if self._eventIsStart(type, info):
            self.eventCache[type][key]['start'] = True
        if self._eventIsEnd(type, info):
            self.eventCache[type][key]['end'] = True
        # if (type == 'illegalOccupation') and (key == 1107720):
        #     print(f'key is {key}, count is {self.eventCache[type][key]["count"]}')
        if beforeEnd and self.eventCache[type][key]['start'] and self.eventCache[type][key]['end']:
            return True
        else:
            return False

    def clearEventCache(self, currentDataTimeStamp: int):
        '''function clearEventCache

        input
        -----
        currentDataTimeStamp: int, 当前数据时间戳, ms单位
        note: 数据时间戳与now函数不一定相同, 以处理的数据时间为标准

        清空缓存, 每次eventRun在外部调用, 用于清空缓存。由eventDetector的eventMng调用。
        '''
        typeKey2Del = []    # 存储需要删除的type和key
        for type, typeCache in self.eventCache.items():
            for key, value in typeCache.items():
                if currentDataTimeStamp - value['time'] > LIMITTIME:
                    typeKey2Del.append((type, key))
        # 删除过期事件
        for type, key in typeKey2Del:
            del self.eventCache[type][key]

    def _getEventRecordKey(self, type, *info):
        '''function _getEventRecordKey
        
        input
        -----
        type: str, 事件类型
        info: any, 事件信息
        
        return
        ------
        key: any, 事件索引

        根据事件类型和事件信息获取事件索引

        # 单车事件: 获取发生事件的车辆id
        # 抛洒物事件: 以车道id+cell order为索引, tuple类型
        # 拥堵事件: 车道id
        # 事故事件: 两个车辆的id, tuple类型
        '''
        info = info[0]  # 传进来的时候会在外边又套一层tuple
        if type in ['stop', 'lowSpeed', 'highSpeed',
                    'EmgcBrake', 'illegalOccupation']:
            key = info[0]['id']
        elif type == 'spill':
            key = (info[0].laneID, info[0].order)
        elif type == 'crowd':
            key = info[0].ID
        elif type == 'incident':
            key = (info[0]['id'], info[1]['id'])
        return key

    def _eventIsStart(self, type, *info):
        '''function _eventIsStart

        input
        -----
        type: str, 事件类型
        info: any, 事件信息

        return
        ------
        isStart: bool, 是否为事件开始

        判断事件是否为开始事件
        '''
        info = info[0]  # 传进来的时候会在外边又套一层tuple
        isStart = False
        if (type in ['spill', 'crowd']) and (info[4] == 'start'):
            isStart = True            
        elif ((type in ['stop', 'lowSpeed', 'highSpeed',
                      'EmgcBrake', 'illegalOccupation']) and
                      (info[2] == 'start')):
            isStart = True
        elif type == 'incident':
            isStart = True
        return isStart

    def _eventIsEnd(self, type, *info):
        '''function _eventIsEnd

        input
        -----
        type: str, 事件类型
        info: any, 事件信息

        return
        ------
        isEnd: bool, 是否为事件结束

        判断事件是否为结束事件。
        对于spill和crowd来说, 在开始时会报警, 在进行时也会报警,
        为了避免进行时出现频繁报警的行为, 因此设置为只要接收到这两个type,
        无论start或end, 均返回True, 表示该事件结束, 抑制频繁报错。
        真正判断两类事件报错, 由_eventIsRealEnd4SpillAndCrowd负责。
        '''
        info = info[0]  # 传进来的时候会在外边又套一层tuple
        isEnd = False
        if (type in ['spill', 'crowd']):    #  and (info[4] == 'end')
            isEnd = True
        elif ((type in ['stop', 'lowSpeed', 'highSpeed',
                      'EmgcBrake', 'illegalOccupation']) and
                      (info[2] == 'end')):
            isEnd = True
        elif type == 'incident':
            isEnd = True
        return isEnd

    def _eventIsRealEnd4SpillAndCrowd(self, type, *info):
        '''function _eventIsRealEnd4SpillAndCrowd

        input
        -----
        None

        return
        ------
        isEnd: bool, 是否为事件结束

        该函数与上一个判断终止的函数不同。
        对于spill和crowd来说, 该情况会判断是否为真正的结束事件。
        '''
        info = info[0]
        isEnd = False
        if (type in ['spill', 'crowd']) and (info[4] == 'end'):
            isEnd = True
        return isEnd
