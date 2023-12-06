class event:
    '''
    事件基础类。不同类型的具体事件以此为基类。
    '''
    def __init__(self, event_name, event_type, event_time, event_location, event_level, event_description):
        self.event_name = event_name
        self.event_type = event_type
        self.event_time = event_time
        self.event_location = event_location
        self.event_level = event_level
        self.event_description = event_description
        self.event_status = 'new'