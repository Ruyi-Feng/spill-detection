import os
from road_calibration import Calibrator
from message_driver import Driver
import pre_processing
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
        传感器数据文件路径, 该参数仅在离线模拟时使用，用于读取离线数据。

    methods
    -------
    startManager(msg): 在完成标定或读取标定后启动管理器。
    calibration(msg):  接受标定数据，更新标定器。
    run(msg):          接受传感器数据，返回发送数据、交通流参数、事件检测结果。

    生成控制器，用于控制整个算法流程。
    '''
    def __init__(self, cfgPath: str, clbPath: str):
        '''function __init__

        input
        -----
        cfgPath: str
            算法参数文件路径
        clbPath: str
            标定参数文件路径

        '''
        # 控制器启动
        self.cfgPath = cfgPath
        self.clbPath = clbPath
        # 配置参数
        cfg = loadConfig(cfgPath)
        self.cfg = cfg
        # 是否标定
        self.needClb = False
        self.clbtor = None
        self.calibFrames = cfg['calib']['calib_seconds'] * cfg['fps']
        self.calibCount = 0
        if not (os.path.exists(clbPath)) | self.cfg['calib']['if_recalib']:
            print('开始标定过程')
            # 没有cfg或者配置需要则标定
            self.needClb = True
            clbtor = Calibrator(clbPath=clbPath, fps=cfg['fps'],
                                laneWidth=cfg['calib']['laneWidth'],
                                emgcWidth=cfg['calib']['emgcWidth'],
                                cellLen=cfg['calib']['cell_len'],
                                qMerge=cfg['calib']['q_merge'])
            self.clbtor = clbtor
        else:   # 有cfg则读取, 不需要标定
            print('开始接收数据')
            self.clb = loadYaml(clbPath)
            self.startManager()

    def calibration(self, msg):
        '''function calibration

        input
        -----
        msg: str | list
            传感器数据, str | list格式。str为传输信息(不处理), list为传感器数据。

        return
        ------
        msg: str | list
            发送数据, str | list格式。str为传输信息(不处理), list为传感器数据。

        接受传感器数据，根据条件判断是否需要标定或结束标定。
        '''
        if self.clbtor.count < self.calibFrames:
            self.clbtor.run(msg)
        else:
            self.clbtor.calibrate()
            self.clbtor.save()
            print('开始接收数据')
            self.clb = loadYaml(self.clbPath)
            # 启动管理器
            self.startManager()
            self.needClb = False

    def startManager(self):
        '''function startManager

        在完成标定或读取标定后启动管理器。
        '''
        # 生成数据驱动器
        self.drv = Driver()
        # 生成事件检测器(内含交通参数管理器)
        self.edt = EventDetector(self.cfg['fps'], self.clb, self.cfg)

    def run(self, msg: list) -> (list, list):
        '''function run

        input
        -----
        msg: str | list, 传感器车辆数据。str为传输信息(不处理), list为传感器数据。

        return
        ------
        msg: str | list, 传感器车辆数据。str为传输信息(不处理), list为传感器数据。
        event: list, 事件检测结果。

        接受传感器数据，返回发送数据、事件检测结果。
        '''
        # 接受数据
        valid, cars = self.drv.receive(msg)
        if not valid:
            return
        # calibration road cells
        if self.needClb:
            self.calibration(cars)
        # 预处理
        cars = pre_processing.preProcess(cars, self.trm)
        # 事件检测(内含交通流参数计算+事件检测)
        event = self.edt.run(cars)
        # 发送数据
        msg = self.drv.send(cars)
        # print(msg)
        return msg, event
