from pre_processing.class_smooth import Smooth
from pre_processing.class_complement import Complement


class targetManager():
    def __init__(self) -> None:
        self.targetList = []            # 存储活跃状态的各ID车辆target
        self.targetsInCurrentFrame = [] # 存储当前帧车辆目标的target
        self.IDsInLastFrame = []        # 存储上一帧车辆目标的ID
        self.IDsInCurrentFrame = []     # 存储当前帧车辆目标的ID
        self.lostIDs = []               # 存储当前帧丢失的ID
        self.newIDs = []                # 存储当前帧新出现的ID
        self.smth = Smooth()
        self.cmp = Complement()

    def recieve(self, msg): 
        '''
        接收当前帧的传感器数据, 与存储的上一帧数据进行比较, 更新除targetList以外的属性(targetList用于补全，平滑的计算)
        '''

    def smooth(self, msg):
        '''do smooth on curr_frame targetList

        

        '''
        x = msg["x"]
        self.smth.run(hist, curr)


    def update(self, msg):
        '''
        接受每帧传输来的目标信息，更新targetList
        '''
        # 更新target
    
    def clean(self, msg):
        '''
        清除targetList中的过期目标
        '''



class target():
    '''
    为每个车辆生成一个target对象，用于记录车辆上一帧的轨迹信息。
    上一帧的轨迹信息将用于：
    1. 检查id跳变并纠正。
    2. 丢失目标轨迹补全。
    3. 车辆轨迹平滑。
    '''
    def __init__(self, carMsg) -> None:
        pass
