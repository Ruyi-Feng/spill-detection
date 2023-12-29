import os
import yaml
from road_calibration import Calibrator
from message_driver import Driver
import pre_processing
from traffic_manager import TrafficMng
from event_detection import EventDetector


class Controller:
    '''class Controller

    properties
    ----------
    configPath: str
        算法参数文件路径
    clbPath: str
        标定参数文件路径
    dataPath: str
        传感器数据文件路径, 该参数仅在离线模拟时使用，用于读取离线数据。

    methods
    -------
    receive(msg)
        接受传感器数据，返回发送数据、交通流参数、事件检测结果。
    calibrate(msg)
        接受标定数据，更新标定器。
    run(msg)
        接受传感器数据，返回发送数据、交通流参数、事件检测结果。
    _loadfile(path)
        读取json文件, 返回dict。
    _saveCalib()
        保存标定结果到clbPath。

    生成控制器，用于控制整个算法流程。
    '''
    def __init__(self, configPath: str, clbPath: str):
        '''function __init__

        input
        -----
        configPath: str
            算法参数文件路径
        clbPath: str
            标定参数文件路径

        '''
        # 控制器启动
        self.configPath = configPath
        self.clbPath = clbPath
        # 算法参数
        config = self._loadyaml(configPath)
        self.config = config
        # 是否标定
        self.needClb = False
        self.clbtor = None
        self.calibFrames = config['calib']['calib_seconds'] * config['fps']
        self.calibCount = 0
        if not (os.path.exists(clbPath)) | self.config['calib']['if_recalib']:
            print('开始标定过程')
            # 没有config或者配置需要则标定
            self.needClb = True
            clbtor = Calibrator(clbPath=clbPath, fps=config['fps'],
                                laneWidth=config['calib']['laneWidth'],
                                emgcWidth=config['calib']['emgcWidth'],
                                cellLen=config['calib']['cell_len'],
                                qMerge=config['calib']['q_merge'])
            self.clbtor = clbtor
        else:   # 有config则读取, 不需要标定
            print('开始接收数据')
            self.clb = self._loadyaml(clbPath)
            self.startManager()

    def _ifNotValid(self, msg) -> bool:
        return (type(msg) == str)

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
        ? traffic: dict
            交通流参数, dict格式。
        ? event: dict
            事件检测结果, dict格式。

        接受传感器数据，返回发送数据、交通流参数、事件检测结果。
        根据条件判断是否需要标定，若需要则标定。
        '''

        if self._ifNotValid(msg):
            return

        if self.clbtor.count < self.calibFrames:
            self.clbtor.receive(msg)
        else:
            self.clbtor.calibrate()
            self.clbtor.save()
            print('开始接收数据')
            self.clb = self._loadyaml(self.clbPath)
            # 启动管理器
            self.startManager()
            self.needClb = False

    def startManager(self):
        '''function startManager

        在完成标定或读取标定后启动管理器。
        '''
        # 生成数据驱动器
        self.drv = Driver()
        # 生成交通管理器
        self.tm = TrafficMng(self.clb, self.config)
        # 生成事件检测器
        self.edt = EventDetector(self.config['fps'], self.clb,
                                 self.config['event']['event_types'],
                                 self.config['event']['v_low'],
                                 self.config['event']['v_high'],
                                 self.config['event']['t_tolerance'],
                                 self.config['event']['q_standard'],
                                 self.config['event']['rate2'],
                                 self.config['event']['d_touch'],
                                 self.config['event']['density_crowd'],
                                 self.config['event']['v_crowd'],
                                 self.config['event']['a_intense'],
                                 self.config['event']['duration_intense'],
                                 self.config['event']['duration_low'],
                                 self.config['event']['duration_high'])

    def receive(self, msg: list):
        # 接受数据
        cars = self.drv.receive(msg)
        # calibration road cells
        if self.needClb:
            self.calibration(cars)
        # 预处理
        cars = pre_processing.preProcess(cars, self.trm)
        # 交通流参数计算
        traffic = self.tm.receive(cars)
        # 事件检测
        cars = self.edt.run(cars, traffic)
        # 发送数据
        msg = self.drv.send(cars)
        # print(msg)

    def _loadyaml(self, path: str) -> dict:
        '''function _loadParam

        input
        -----
        path: str
            文件路径

        return
        ------
        config: dict
            配置参数
        '''
        with open(path, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return config
