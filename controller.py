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
                 logger: MyLogger, args, ifReportRunTime: bool = False):
        '''function __init__

        input
        -----
        cfgPath: str, 算法参数文件路径
        clbPath: str, 标定参数文件路径
        logger: MyLogger, 日志器
        args: dict, 参数
        ifReportRunTime: bool, 是否报告各阶段运行时间
        '''
        self.ifReportRunTime = ifReportRunTime
        self.timeTmp = [[] for _ in range(7)]

        # 读取配置
        self.cfgPath = cfgPath
        cfg = loadConfig(cfgPath)
        self.cfg = cfg
        # 生成日志器
        self.logger = logger
        self.deviceID = args.deviceId
        self.deviceType = args.deviceType
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
            txt1 = f'{clbPath}文件已存在, ' if os.path.exists(clbPath) \
                else f'{clbPath}文件不存在, '
            txt2 = '配置设置需要进行标定, ' if self.cfg['ifRecalib'] \
                else '配置设置不需重复标定（若文件已存在）'
            self.logger.info(txt1 + txt2)
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
                                qMerge=cfg['qMerge'])
            self.clbtor = clbtor
        else:   # 有cfg则读取, 不需要标定
            txt = f'{clbPath}文件已存在, 且配置设置不需重复标定'
            self.logger.info(txt)
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
        time1 = time.time()
        valid, cars = self.drv.receive(msg)
        if not valid:
            return None, None
        # 接收标定
        if self.needClb:
            self.calibration(cars)
            return None, None
        time2 = time.time()
        # 更新缓存
        self._updateCache(cars)
        time3 = time.time()
        # 预处理
        cars = self.pp.run(cars)
        time4 = time.time()
        # 事件检测(内含交通流参数计算+事件检测)
        events = self.edt.run(cars)
        time5 = time.time()
        # 发送数据
        msg, events = self.drv.send(cars.copy(), events)
        time6 = time.time()
        # 保存缓存
        if len(events) > 0:
            for event in events:
                self._saveCache(event['eventID'])
        time7 = time.time()
        # 计算各阶段时长
        if self.ifReportRunTime:
            timeDriver = time2 - time1
            timeTraffic = time3 - time2
            timePre = time4 - time3
            timeDetect = time5 - time4
            timeSend = time6 - time5
            timeSave = time7 - time6
            timeTotal = time7 - time1
            self.timeTmp[0].append(timeDriver)
            self.timeTmp[1].append(timeTraffic)
            self.timeTmp[2].append(timePre)
            self.timeTmp[3].append(timeDetect)
            self.timeTmp[4].append(timeSend)
            self.timeTmp[5].append(timeSave)
            self.timeTmp[6].append(timeTotal)
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
        sonDir = f'{dir}/{self.deviceID}_{self.deviceType}'
        if not os.path.exists(sonDir):
            os.makedirs(sonDir)

        path = f'{sonDir}/{eventID}.txt'
        with open(path, 'w') as f:
            for msg in self.cache:
                f.write(str(msg) + '\n')

    def reportRunTime(self, seconds: float):
        '''计算各阶段总耗用和平均耗用时长, 以及各阶段的时长占比，并输出'''
        # 总耗
        timeDriver = sum(self.timeTmp[0])
        timeTraffic = sum(self.timeTmp[1])
        timePre = sum(self.timeTmp[2])
        timeDetect = sum(self.timeTmp[3])
        timeSend = sum(self.timeTmp[4])
        timeSave = sum(self.timeTmp[5])
        timeTotal = sum(self.timeTmp[6])
        if timeTotal == 0:
            return   # 说明该设备数据为空, controller未接收数据
        # 平均耗
        avgDriver = timeDriver / seconds
        avgTraffic = timeTraffic / seconds
        avgPre = timePre / seconds
        avgDetect = timeDetect / seconds
        avgSend = timeSend / seconds
        avgSave = timeSave / seconds
        avgTotal = timeTotal / seconds
        # 占比
        percentDriver = timeDriver / timeTotal
        percentTraffic = timeTraffic / timeTotal
        percentPre = timePre / timeTotal
        percentDetect = timeDetect / timeTotal
        percentSend = timeSend / timeTotal
        percentSave = timeSave / timeTotal
        # print输出, ms单位
        print('驱动器平均耗时: {:.2f}ms, 占比: {:.2%}'.format(avgDriver * 1000, percentDriver))
        print('交通参数计算平均耗时: {:.2f}ms, 占比: {:.2%}'.format(avgTraffic * 1000, percentTraffic))
        print('预处理平均耗时: {:.2f}ms, 占比: {:.2%}'.format(avgPre * 1000, percentPre))
        print('事件检测平均耗时: {:.2f}ms, 占比: {:.2%}'.format(avgDetect * 1000, percentDetect))
        print('发送平均耗时: {:.2f}ms, 占比: {:.2%}'.format(avgSend * 1000, percentSend))
        print('保存平均耗时: {:.2f}ms, 占比: {:.2%}'.format(avgSave * 1000, percentSave))
        print('平均总耗时: {:.2f}ms'.format(avgTotal * 1000))
        print('总耗时: {:.2f}ms'.format(timeTotal * 1000))
