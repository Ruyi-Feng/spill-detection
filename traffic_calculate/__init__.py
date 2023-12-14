class TrafficManager():
    '''class TrafficManager

    交通流计算类，根据传感器信息计算交通流

    Attributes
    ----------
    qd: float
        QDuration, 用于计算小时交通流量的流量采样时长
    itv: float
        interval, 更新计算交通参数的间隔时间
    fps: float
        frequency per second, 传感器采样频率

    vcache: list
        vehicle cache, 用于存储车辆目标信息, list每个元素代表一帧接收的数据, 元素格式为dict。
        每帧dict中, 按照lane索引, 存储对应车道上的speed构成的list。
    count: int
        接收计数, 计算时若未达到qd等其他计算需求, 手动进行比例计算
    KeyFrame: int
        关键帧，标记小时交通流量的计算点
    Q: float
        存储路段级交通流量
    q: dict
        存储车道级交通流量
    k: dict
        存储车道级密度
    v: dict
        存储车道级平均速度

    '''
    def __init__(self, fps: float, qd: float, itv: float):
        '''function __init__
        input
        -----
        qd: float
            QDuration, 用于计算小时交通流量的流量采样时长
        itv: float
            interval, 更新计算交通参数的间隔时间
        fps: float
            frequency per second, 传感器采样频率

        '''
        # 参数
        self.qd = qd        # 用于计算小时交通流量的流量采样时长
        self.itv = itv      # 更新计算交通参数的间隔时间
        self.fps = fps      # 传感器采样频率
        # 状态属性
        self.count = 0      # 接收计数，计算时若未达到qd等其他计算需求，手动进行比例计算
        # 车辆目标暂存属性
        self.vcache = []      # 车辆目标暂存属性，用于存储车辆目标信息
        # 交通流属性
        self.KeyFrame = 0   # 关键帧，标记小时交通流量的计算点
        self.Q = 0     # 存储路段级交通流量
        self.q = dict()    # 存储车道级交通流量
        self.k = dict()    # 存储车道级密度
        self.v = dict()    # 存储车道级平均速度

    def receive(self, msg):
        '''function receive

        input
        -----
        msg: list, 传感器数据, msg元素为代表一个车辆目标的dict。

        接收传感器数据, 按照lane存储speed属性, 用于计算交通流参数。
        '''
        # 分缓存数据的长度是否达到了计算交通流参数的要求

    def calculate(self, msg) -> tuple:
        '''function calculate

        input
        -----
        msg: list
            传感器数据

        return
        ------
        traffic:
            存储交通流信息

        根据所传输来的检测信息，计算交通流信息：
        1. 路段级交通流量
        2. 车道级交通流量
        3. 车道级平均速度
        4. 车道级密度
        '''
        traffic = []
        return traffic
