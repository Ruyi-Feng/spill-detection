import os
from road_calibration import Calibrator
from message_driver import Driver
from pre_processing import PreProcessor
from event_detection import EventDetector
from utils import loadConfig, loadYaml


'''Controller is to control the whole process of the project.'''


class Controller:
    '''class Controller

    properties
    ----------
    cfgPath: str
        算法参数文件路径
    clbPath: str
        标定参数文件路径
    dataPath: str
        传感器数据文件路径, 该参数仅在离线模拟时使用, 用于读取离线数据。

    methods
    -------
    startManager(msg): 在完成标定或读取标定后启动管理器。
    calibration(msg):  接受标定数据, 更新标定器。
    run(msg):          接受传感器数据, 返回发送数据、交通流参数、事件检测结果。

    生成控制器, 用于控制整个算法流程。
    '''
    def __init__(self, cfgPath: str, clbPath: str):
        '''function __init__

        input
        -----
        cfgPath: str, 算法参数文件路径
        clbPath: str, 标定参数文件路径
        '''
        # 读取配置
        self.cfgPath = cfgPath
        cfg = loadConfig(cfgPath)
        self.cfg = cfg
        # 生成数据驱动器
        self.drv = Driver()
        # 是否标定
        self.clbPath = clbPath
        self.needClb = False
        self.clbtor = None
        self.calibFrames = cfg['calibSeconds'] * cfg['fps']
        self.calibCount = 0
        if not (os.path.exists(clbPath)) | self.cfg['ifRecalib']:
            print('******开始标定过程******')
            # 没有cfg或者配置需要则标定
            self.needClb = True
            clbtor = Calibrator(clbPath=clbPath, fps=cfg['fps'],
                                laneWidth=cfg['laneWidth'],
                                emgcWidth=cfg['emgcWidth'],
                                cellLen=cfg['cellLen'],
                                qMerge=cfg['qMerge'])
            self.clbtor = clbtor
        else:   # 有cfg则读取, 不需要标定
            print('******开始接收数据******')
            self.clb = loadYaml(clbPath)
            self.startDetect()

    def calibration(self, cars: list):
        '''function calibration

        input
        -----
        cars: list, 某一帧的车辆目标数据, list格式。

        return
        ------
        cars: list, 某一帧的车辆目标数据, list格式。

        进行标定, 存储标定所需数据, 达到标定需求时长后计算标定结果。
        '''
        if self.clbtor.count < self.calibFrames:
            self.clbtor.run(cars)
        else:
            self.needClb = False
            self.clbtor.calibrate()
            self.clbtor.save()
            print('******开始接收数据******')
            self.clb = loadYaml(self.clbPath)
            self.startDetect()   # 凯奇事件检测

    def startDetect(self):
        '''function startManager

        在完成标定或读取标定后正式启动事件检测。
        '''
        # 生成数据预处理器
        self.pp = PreProcessor(self.cfg['maxCompleteTime'], self.cfg['smoothAlpha'])
        # 生成事件检测器(内含交通参数管理器)
        self.edt = EventDetector(self.clb, self.cfg)

    def run(self, msg: list) -> (list, list):
        '''function run

        input
        -----
        msg: str | list, 传感器车辆数据。str为传输信息(不处理), list为传感器数据。

        return
        ------
        msg: list, 某一帧的车辆目标数据, list格式。
        events: list, 事件检测结果。

        接受传感器数据, 返回发送数据、事件检测结果。
        '''
        # 接受数据
        valid, cars = self.drv.receive(msg)
        if not valid:
            return None, None
        # 接收标定
        if self.needClb:
            self.calibration(cars)
            return None, None
        # 预处理
        cars = self.pp.run(cars)
        # 事件检测(内含交通流参数计算+事件检测)
        events = self.edt.run(cars)
        # 发送数据
        msg, events = self.drv.send(cars.copy(), events)
        return msg, events
