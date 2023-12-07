import os
import json

from calibration import Calibrator
from msg_driver import receive, send
import pre_processing
from traffic_calculate import TrafficManager
from event_detection import event_detection

class Controller:
    '''class Controller
    
    properties
    ----------
    configPath: str
        算法参数文件路径
    calibrationPath: str
        标定参数文件路径
    dataPath: str
        传感器数据文件路径, 该参数仅在离线模拟时使用，用于读取离线数据。

    '''
    def __init__(self, configPath: str, calibrationPath: str, dataPath: str = None):
        '''function __init__
        
        input
        -----
        configPath: str
            算法参数文件路径
        calibrationPath: str
            标定参数文件路径
        dataPath: str
            传感器数据文件路径, 该参数仅在离线模拟时使用，用于读取离线数据。
        
        '''
        # 控制器启动
        self.configPath = configPath
        self.calibrationPath = calibrationPath
        self.dataPath = dataPath
        # 算法参数
        config = self._loadfile(configPath)
        self.config = config
        # 是否标定
        self.needClb = False
        if not(os.path.exists('./calibration/calib.json')) | self.config['if_recalibrate']:    # 没有config或者配置需要则标定
            self.needClb = True
            clbtor = Calibrator()
            self.clbtor = clbtor
        else:   # 有config则读取, 不需要标定
            clb = self._loadfile(calibrationPath)
            self.clb = clb
        # 运行管理器
        tfm = TrafficManager()
        self.tfm = tfm

    def receive(self, msg):
        '''function receive

        input
        -----
        msg: str
            传感器数据, str格式。

        return
        ------
        msg: str
            发送数据, str格式。
        traffic: dict
            交通流参数, dict格式。
        event: dict
            事件检测结果, dict格式。

        接受传感器数据，返回发送数据、交通流参数、事件检测结果。
        '''
        try:
            data = json.loads(data) # 接收到list数据
        except:
            pass    # 非检测信息则会接收到str数据
    
    def calibrate(self, msg: list):
        '''function calibrate
        
        '''
        
        self.clbtor.recieve(msg)
        
            
    def run(self, msg: list):
        # 接受数据
        msg = receive.recieve(msg)
        # 预处理
        msg, traffic = pre_processing.preProcess(msg, traffic)
        # 交通流参数计算
        traffic = pre_processing.traffic_calculate(msg, traffic)
        # 事件检测
        msg = event_detection(msg)
        # 发送数据
        msg = send.send(msg)
        # print(msg)



    def _loadfile(self, path: str) -> dict:
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
            config = json.load(f)
        return config

    def _saveCalib(self):
        config = self.clbtor.calibration
        self.clbtor.save('./calibration/calib.json')