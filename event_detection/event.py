'''This is to define the event class.'''

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
    '''
    def __init__(self):
        '''function __init__

        初始化事件管理器
        '''
        self.eventTypes = ["spill", "stop", "lowSpeed", "highSpeed",
                       "emergencyBrake", "incident", "crowd",
                       "illegalOccupation"]
        typeIdDict = {self.eventTypes[i]: i for i in 
                      range(len(self.eventTypes))}
        self.events = {}    # TODO 定义统一结构

    def run():
        '''function run

        执行事件管理, 将事件信息添加到events中
        '''
        pass

    def clear():
        '''function clear
        
        清空events, 在每帧结束后调用, 以清空
        '''
        pass
