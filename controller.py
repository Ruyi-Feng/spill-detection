import os
import time
from logger import MyLogger
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
    cfgPath: str, 算法参数文件路径
    clbPath: str, 标定参数文件路径
    dataPath: str, 传感器数据文件路径, 该参数仅在离线模拟时使用, 用于读取离线数据。
    cfg: dict, 算法参数

    needClb: bool, 是否需要标定
    calibFrames: int, 标定所需帧数
    calibCount: int, 当前标定帧数
    clb: dict, 标定参数

    logger: MyLogger, 日志器
    drv: Driver, 数据驱动器
    clbtor: Calibrator, 标定器
    pp: PreProcessor, 数据预处理器
    edt: EventDetector, 事件检测器
    cache: 缓存指定时间的数据

    methods
    -------
    startManager(msg): 在完成标定或读取标定后启动管理器。
    calibration(msg):  接受标定数据, 更新标定器。
    run(msg):          接受传感器数据, 返回发送数据、交通流参数、事件检测结果。

    生成控制器, 用于控制整个算法流程。
    '''
    def __init__(self, cfgPath: str, clbPath: str,
                 logger: MyLogger):
        '''function __init__

        input
        -----
        cfgPath: str, 算法参数文件路径
        clbPath: str, 标定参数文件路径
        logger: MyLogger, 日志器
        '''
        # 读取配置
        self.cfgPath = cfgPath
        cfg = loadConfig(cfgPath)
        self.cfg = cfg
        # 生成日志器
        self.logger = logger
        # 生成数据驱动器
        self.drv = Driver(cfg['fps'], logger)
        # 是否标定
        self.clbPath = clbPath
        self.needClb = False
        self.clbtor = None
        self.calibFrames = cfg['calibSeconds'] * cfg['fps']
        self.calibCount = 0
        if (not (os.path.exists(clbPath))) | self.cfg['ifRecalib']:
            startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                time.time() + cfg['calibSeconds']))
            self.logger.info('******开始标定过程******' +
                             f"开始时刻: {startTime}," +
                             f"标定时长: {cfg['calibSeconds']}s," +
                             f"预计结束时刻: {endTime}")
            # 没有cfg或者配置需要则标定
            self.needClb = True
            clbtor = Calibrator(clbPath=clbPath, fps=cfg['fps'],
                                laneWidth=cfg['laneWidth'],
                                emgcWidth=cfg['emgcWidth'],
                                cellLen=cfg['cellLen'],
                                qMerge=cfg['qMerge'],
                                logger=logger)
            self.clbtor = clbtor
        else:   # 有cfg则读取, 不需要标定
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
            self.logger.info('******标定完成******' +
                             '完成时刻: {}'.format(
                                 time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime())))
            self.clbtor.calibrate()
            self.clbtor.save()
            self.clb = loadYaml(self.clbPath)
            self.startDetect()   # 凯奇事件检测

    def startDetect(self):
        '''function startManager

        在完成标定或读取标定后正式启动事件检测。
        '''
        self.logger.info('******开始事件检测******' +
                         '开始时刻: {}'.format(
                             time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.localtime())))
        self._initCache()
        # driver接收当前路段的lanes列表
        self.drv.setLanes(list(self.clb.keys()))
        # 生成数据预处理器
        self.pp = PreProcessor(self.cfg['maxCompleteTime'],
                               self.cfg['smoothAlpha'])
        # 生成事件检测器(内含交通参数管理器)
        self.edt = EventDetector(self.clb, self.cfg, self.logger)

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
        # 更新缓存
        self._updateCache(cars)
        # 预处理
        cars = self.pp.run(cars)
        # 事件检测(内含交通流参数计算+事件检测)
        events = self.edt.run(cars)
        # 发送数据
        msg, events = self.drv.send(cars.copy(), events)
        # 保存缓存
        if len(events) > 0:
            for event in events:
                self._saveCache(event['eventID'])

        return msg, events

    def _initCache(self):
        '''function _initCache

        初始化缓存
        '''
        self.cacheNum = self.cfg['cacheSeconds'] * self.cfg['fps']
        self.cache = []

    def _updateCache(self, msg: list):
        '''function _updateCache

        input
        -----
        msg: list, 传感器数据

        更新缓存
        '''
        self.cache.append(msg)
        if len(self.cache) > self.cacheNum:
            self.cache.pop(0)

    def _saveCache(self, eventID: str):
        '''function _saveCache

        input
        -----
        path: str, 缓存文件路径

        保存缓存
        '''
        dir = './logger/eventsCache'
        if not os.path.exists(dir):
            os.makedirs(dir)
        path = f'{dir}/{eventID}.txt'
        with open(path, 'w') as f:
            for msg in self.cache:
                f.write(str(msg) + '\n')
