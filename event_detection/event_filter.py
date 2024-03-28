from utils.default import defaultEventTypes


LIMITTIME = 3 * 60 * 1000   # 3分钟, ms单位, 若超过3分钟则重新报警, 暂不启用


class EventFilter():
    '''class EventFilter

    编程便捷的角度对事件进行过滤, 
    当前会出现同一id的同一事件会多次报警的情况,
    限制在3分钟内事件开始和事件结束只报警一次。
    实现操作: 同一id同一type事件报警两次后, 开始限制3分钟。
    # TODO 频繁事件发生会导致eventID过号, 事件ID会拉满, 需要将filter机制加入到event生成中
    加入到pipeline的最后,driver之前。
    '''
    def __init__(self):
        '''
        缓存组织形式
        {
            'type': {
                'id': {
                    'count': int,
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
        - 当type为'spill'时, info为[cellMng, deviceID, deviceType, eventID]
        # 对应
        - 当type为'stop', 'lowSpeed', 'highSpeed', 'EmgcBrake',
          'illegalOccupation'时, info为[car, eventID]
        - 当type为'incident'时, info为[car1, car2]
        - 当type为'crowd'时, info为[laneMng, deviceID, deviceType, eventID]

        return
        ------
        ifFilter: bool, 是否需要过滤

        返回该事件是否近期已经被报警, 如果已经报警, 则需要过滤返回True
        '''
        info = info[0]  # 传进来的时候会在外边又套一层tuple
        # 获取当前事件最新的时间戳
        timestamp = max(startTime, endTime)  # 可能endTime是-1
        # 获取列表索引
        # 单车事件：获取发生事件的车辆id
        # 抛洒物事件：以车道id+cell order为索引, tuple类型
        # 拥堵事件：车道id
        # 事故事件：两个车辆的id, tuple类型
        if type in ['stop', 'lowSpeed', 'highSpeed',
                    'EmgcBrake', 'illegalOccupation']:
            key = info[0]['id']
        elif type == 'spill':
            key = (info[0].laneID, info[0].order)
        elif type == 'crowd':
            key = info[0].ID
        elif type == 'incident':
            key = (info[0]['id'], info[1]['id'])

        # 检查cache中是否有该id的该type事件
        if key in self.eventCache[type]:
            # 若有，则更新对应count和time
            self.eventCache[type][key]['count'] += 1
            self.eventCache[type][key]['time'] = timestamp
        else:
            # 若没有，则新增
            self.eventCache[type][key] = {
                'count': 1,
                'time': timestamp
            }
        # 若count>=2, 则返回True
        if self.eventCache[type][key]['count'] >= 2:
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
