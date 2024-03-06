import logging
import os
from datetime import datetime


'''This file defines the logger for the project'''


class MyLogger(logging.Logger):
    '''class MyLogger
    This class is a subclass of the logging.Logger class.
    It is used to create a custom logger for the project'''
    def __init__(self, deviceID: str, deviceType: int, level=logging.INFO):
        '''function __init__

        input
        -----
        deviceID: str, 设备ID
        deviceType: int, 设备类型
        level: int, 日志器级别, 默认为logging.INFO
        '''
        loggerName = deviceID + '_' + str(deviceType)
        super().__init__(loggerName, level)
        self.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s')
        self.formatter = formatter
        # 控制台日志
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(level)
        self.addHandler(ch)
        # 文件日志
        self._checkLogsDir()    # 判断两层文件夹是否存在
        filePath = f'./logger/logs/{loggerName}/{datetime.now().strftime("%Y-%m-%d")}.log'
        fh = logging.FileHandler(filePath)
        fh.setFormatter(formatter)
        fh.setLevel(logging.WARNING)
        self.addHandler(fh)

    def newFileLog(self):
        '''function newFileLog

        每天12点, 更新一个文件保存当天的log'''
        # 判断当天的文件是否存在
        self._checkLogsDir()        # 判断两层文件夹是否存在
        filePath = f'./logger/logs/{self.name}/{datetime.now().strftime("%Y-%m-%d")}.log'
        if os.path.exists(filePath):    # 如果存在，则不需要更新
            return
        # 移除旧的 FileHandler
        for handler in self.handlers[:]:  # 使用切片复制列表，避免在遍历过程中修改列表
            if isinstance(handler, logging.FileHandler):
                self.removeHandler(handler)
        # 文件日志
        fh = logging.FileHandler(filePath)
        fh.setFormatter(self.formatter)
        fh.setLevel(logging.WARNING)
        self.addHandler(fh)
        return

    def _checkLogsDir(self):
        '''function _checkLogsDir

        检查日志文件夹是否存在，不存在则创建'''
        logsDir = './logger/logs'
        if not os.path.exists(logsDir):
            os.mkdir(logsDir)
        deviceDir = f'{logsDir}/{self.name}'
        if not os.path.exists(deviceDir):
            os.mkdir(deviceDir)
