import os
import yaml

from calibration import Calibrator
from msg_driver import Driver
import pre_processing
from traffic import TrafficManager
from detection import EventDetector


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
        if not (os.path.exists(clbPath)) | self.config['calib']['if_recalib']:
            # 没有config或者配置需要则标定
            self.needClb = True
            clbtor = Calibrator(clbPath=clbPath)
            self.clbtor = clbtor
        else:   # 有config则读取, 不需要标定
            clb = self._loadyaml(clbPath)
            self.clb = clb

    def receive(self, msg):
        '''function receive

        input
        -----
        msg: str | list
            传感器数据, str | list格式。str为传输信息(不处理), list为传感器数据。

        return
        ------
        msg: str | list
            发送数据, str | list格式。str为传输信息(不处理), list为传感器数据。
        traffic: dict
            交通流参数, dict格式。
        event: dict
            事件检测结果, dict格式。

        接受传感器数据，返回发送数据、交通流参数、事件检测结果。
        '''
        if type(msg) == str:
            return msg, None, None
        return msg, None, None

    def calibrate(self, msg: list):
        '''function calibrate

        '''

        self.clbtor.recieve(msg)

    def startManager(self):
        '''function startManager

        在完成标定或读取标定后启动管理器。
        '''
        # 运行管理器
        drv = Driver()
        self.drv = drv
        tfm = TrafficManager(self.config['fps'],
                             self.config['q_cal_duration'],
                             self.config['cal_interval'])
        self.tfm = tfm
        edt = EventDetector(self.config['fps'], self.clb,
                            self.config['event_types'],
                            self.config['vl'], self.config['vh'],
                            self.config['tt'], self.config['r2'],
                            self.config['dt'],
                            self.config['dstc'], self.config['vc'],
                            self.config['ai'], self.config['di'],
                            self.config['dl'], self.config['dh'])
        self.edt = edt

    def run(self, msg: list):
        # 接受数据
        msg = self.drv.recieve(msg)
        # 预处理
        msg, traffic = pre_processing.preProcess(msg, self.trm)
        # 交通流参数计算
        traffic = pre_processing.traffic_calculate(msg, self.trm)
        # 事件检测
        msg = self.edt.run(msg, traffic)
        # 发送数据
        msg = self.drv.send.send(msg)
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

    def _saveCalib(self):
        # config = self.clbtor.calibration
        self.clbtor.save(self.clbPath)
