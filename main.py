import os
import sys
import argparse
import json
from datetime import datetime
from controller import Controller
from kafka import KafkaConsumer
from connector import HttpPoster
from rsu_simulator import Smltor, DfSimulator
from logger import MyLogger
from utils import loadConfig, isNotTargetDevice, isInvalidMsg
from utils import checkConfigDevices, argsFromDeviceID
from utils import unixMilliseconds2Datetime


if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = 'six.moves'


def params():
    parser = argparse.ArgumentParser(description='spill-detection parameters')
    parser.add_argument('--deviceId', default='K00+000',
                        type=str, help="K73+516")
    parser.add_argument('--deviceType', type=int, default=0,
                        help="radar 1, camera 2")
    args = parser.parse_args()
    return args


def simulatedMain():
    configPath = './config.yml'
    clbPath = './road_calibration/clbymls/clb.yml'
    dataPath = './data/result.txt'
    # clbPath = './road_calibration/clbymls/clb_K81+866_1.yml'
    # dataPath = r'D:\myscripts\spill-detection\data\sample\stop20240326-K81+866.csv'
    args = params()
    logger = MyLogger(args.deviceId, args.deviceType)
    controller = Controller(configPath, clbPath, logger, args)
    smltor = Smltor(dataPath) if dataPath.endswith('.txt') else DfSimulator(dataPath)

    # 模拟接受数据
    while True:
        msg = smltor.run()
        # print(msg)
        if msg == '':   # 读取到文件末尾
            break
        msg, events = controller.run(msg)  # msg为控制器返回的需要发送的数据


def main():
    '''function main

    单进程, 单设备, 可在外部起多进程
    部署版本的主函数
    '''
    args = params()
    deviceName = args.deviceId + '_' + str(args.deviceType)
    logger = MyLogger(args.deviceId, args.deviceType)
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    # 生成kafka消费者
    kc = KafkaConsumer(
        cfg['topic'], bootstrap_servers=cfg['ip'],
        api_version=tuple(cfg['producerversion']),
        group_id=deviceName,
        # auto_offset_reset='smallest',
        # auto_offset_reset='latest',
        # auto_commit_interval_ms=cfg['kafkaAutoCommitIntervalMs']
        )
    # 生成http上报器
    hp = HttpPoster(cfg['http'])
    logger.info('kafka与http数据通信组件已生成.')

    # 获取当前设备信息
    logger.info('waiting the first message to obtain device information...')
    for msgBytes in kc:     # 从kafka接收一帧数据以确定当前设备的信息
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        if isInvalidMsg(msg) or isNotTargetDevice(msg, args):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        logger.info('接收该设备数据: deviceID:' + deviceID +
                    'deviceType:' + deviceType)
        break

    # 根据设备信息生成clbPath, 为./road_calibration/clb_设备名_设备类型.yml
    # 生成主控制器
    clbPath = './road_calibration/clbymls/clb_' + \
        deviceID + '_' + deviceType + '.yml'
    controller = Controller(configPath, clbPath, logger, args)
    logger.info('算法组件生成成功, 数据进入算法通道.')

    # 持续性运行接收
    for msgBytes in kc:
        # 数据解码
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        # 非空数据判断
        if isInvalidMsg(msg) or isNotTargetDevice(msg, args):
            continue
        if (len(msg) == 0) or (len(msg['targets']) == 0):
            continue
        dataTime = unixMilliseconds2Datetime(msg['targets'][0]['timestamp'])
        print('latest receiving time:', datetime.now(),
              ' dataTime: ', dataTime,
              f'{args.deviceId}_{args.deviceType}', end='\r')
        # log文件保存更新
        logger.updateDayLogFile()
        # 算法检测
        msg, events = controller.run(msg)
        if (events is None) or (len(events) == 0):
            continue    # 未检测到事件
        # 上报事件
        hp.run(events)


def simulatedMainGrouped(dataPath: str):
    '''多设备组合的主函数, 用于从离线数据读取进行测试'''
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    condition, hint = checkConfigDevices(cfg)
    if not condition:
        print(hint)
        return

    # 数据地址
    smltor = Smltor(dataPath)

    # 根据设备信息生成clbPath, 为./road_calibration/clb_设备名_设备类型.yml
    # 生成主控制器
    controllerGroup = {}
    for dID, dType in zip(cfg['deviceIDs'], cfg['deviceTypes']):
        name = dID + '_' + str(dType)       # 桩号+设备类型
        clbPath = './road_calibration/clbymls/clb_' + name + '.yml'
        logger4Device = MyLogger(dID, dType)
        args = argsFromDeviceID(dID, dType)
        controllerGroup[name] = Controller(configPath, clbPath,
                                           logger4Device, args,
                                           ifReportRunTime=False)
    print('算法组件生成成功, 数据进入算法通道.')
    # 持续性运行接收
    # 模拟接受数据
    count = 0
    while True:
        count += 1
        # if count > 12000:       # 以该段时间测试运行速度
        #     break
        msg = smltor.run()
        if msg == '':   # 读取到文件末尾
            break
        # 非空数据判断
        if isInvalidMsg(msg):
            continue
        if (len(msg) == 0) or (len(msg['targets']) == 0):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        name = deviceID + '_' + deviceType
        dataTime = unixMilliseconds2Datetime(msg['targets'][0]['timestamp'])
        print('latest receiving time:', datetime.now(),
              ' dataTime: ', dataTime, name, end='\r')   # 持续显示

        # 当前消息的设备
        if name not in controllerGroup:
            print('该设备未在config中设置, 请添加.' + name)
            continue
        # log文件保存更新
        controllerGroup[name].logger.updateDayLogFile()
        # 算法检测
        msg, events = controllerGroup[name].run(msg)
    # 各controller报告运行时间
    # for name in controllerGroup:
    #     print(name, 'time report:')
    #     controllerGroup[name].reportRunTime()


def simulatedMainGroupedMultiThread(dataPath: str):
    '''多设备组合的主函数, 用于从离线数据读取进行测试'''
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    condition, hint = checkConfigDevices(cfg)
    if not condition:
        print(hint)
        return

    # 数据地址
    smltor = Smltor(dataPath)

    # 根据设备信息生成clbPath, 为./road_calibration/clb_设备名_设备类型.yml
    # 生成主控制器
    controllerGroup = {}
    for dID, dType in zip(cfg['deviceIDs'], cfg['deviceTypes']):
        name = dID + '_' + str(dType)       # 桩号+设备类型
        clbPath = './road_calibration/clbymls/clb_' + name + '.yml'
        logger4Device = MyLogger(dID, dType)
        args = argsFromDeviceID(dID, dType)
        controllerGroup[name] = Controller(configPath, clbPath,
                                           logger4Device, args,
                                           ifReportRunTime=True)
    print('算法组件生成成功, 数据进入算法通道.')
    # 持续性运行接收
    # 模拟接受数据
    count = 0
    import threading
    while True:
        count += 1
        # if count > 12000:       # 以该段时间测试运行速度
        #     break
        msg = smltor.run()
        if msg == '':   # 读取到文件末尾
            break
        # 非空数据判断
        if isInvalidMsg(msg):
            continue
        if (len(msg) == 0) or (len(msg['targets']) == 0):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        name = deviceID + '_' + deviceType
        dataTime = unixMilliseconds2Datetime(msg['targets'][0]['timestamp'])
        print('latest receiving time:', datetime.now(),
              ' dataTime: ', dataTime, name, end='\r')   # 持续显示

        # 当前消息的设备
        if name not in controllerGroup:
            print('该设备未在config中设置, 请添加.' + name)
            continue
        # log文件保存更新
        controllerGroup[name].logger.updateDayLogFile()
        # 算法检测
        # msg, events = controllerGroup[name].run(msg)
        def runController(controller):
            controller.run(msg)
        t = threading.Thread(target=runController, args=(controllerGroup[name],))
        t.start()
        # if (count % 6000 == 0) & (deviceID == 'K81+320'):
        #     print('time report:', name)
        #     controllerGroup[name].reportRunTime()
    # 各controller报告运行时间
    # for name in controllerGroup:
    #     print(name, 'time report:')
    #     controllerGroup[name].reportRunTime()


def evaluateDeployedModel():
    '''function evaluateDeployedModel

    读取从部署地点的实时保存数据文件,
    模拟实时接收数据, 检验事件结果,
    评估部署模型的性能。
    '''
    # dataDir = './data/'
    # dataDir = r'D:\东南大学\科研\金科\data'
    # dataDir = r'D:\myscripts\spill-detection\data\extractedData'
    # dataDir = r'D:\东南大学\科研\金科\data\dataRy\data'
    dataDir = r'E:\data'
    # dataDir = r'D:\myscripts\spill-detection\data\extractedData\4月22，23日平台告警时间段数据'
    # targetEvaluateFiles = [
    #     # 'K81+320_1_2024-04-23-06-51-34_2024-04-23-06-53-34.txt',
    #     # 'K81+320_1_2024-04-22-17-02-06_2024-04-22-17-04-06.txt'
    #     # 'K81+866_1_2024-04-23-15-00-04_2024-04-23-15-02-04.txt'
    #     # r'K73+516_1_2024-04-23-15-00-59_2024-04-23-15-02-59.txt'
    #     '2024-4-22-19.txt'
    # ]
    for file in os.listdir(dataDir):
        if (
            ('dump' in file) or
            ('result' in file) or
            ('heartbeat' in file) or
            (not file.endswith('.txt'))
            ):
            continue
        # if file not in targetEvaluateFiles:
        #     continue
        print(file, 'is running.')
        simulatedMainGrouped(dataDir + '/' + file)
        # simulatedMainGroupedMultiThread(dataDir + '/' + file)


def mainGrouped():
    '''单进程, 多设备组合的主函数
    因所有设备在同一个代码中运行, 且未区分consumer, 当前弃用
    '''
    logger = MyLogger('main', 'noDeivce')
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    condition, hint = checkConfigDevices(cfg)
    if not condition:
        logger.error(hint)
        return
    # 生成kafka消费者
    kc = KafkaConsumer(
        cfg['topic'], bootstrap_servers=cfg['ip'],
        api_version=tuple(cfg['producerversion']),
        group_id=cfg['groupid'])
    # 生成http上报器
    hp = HttpPoster(cfg['http'])
    logger.info('kafka与http数据通信组件已生成.')

    # 根据设备信息生成clbPath, 为./road_calibration/clb_设备名_设备类型.yml
    # 生成主控制器
    controllerGroup = {}
    for dID, dType in zip(cfg['deviceIDs'], cfg['deviceTypes']):
        name = dID + '_' + str(dType)       # 桩号+设备类型
        clbPath = './road_calibration/clbymls/clb_' + name + '.yml'
        logger4Device = MyLogger(dID, dType)
        args = argsFromDeviceID(dID, dType)
        controllerGroup[name] = Controller(configPath, clbPath,
                                           logger4Device, args)
    logger.info('算法组件生成成功, 数据进入算法通道.')

    # 持续性运行接收
    for msgBytes in kc:
        # 数据解码
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        # 非空数据判断
        if isInvalidMsg(msg):   # 注意顺序, 在msg获取deviceID等属性前判断, 防止报错
            continue
        if (len(msg) == 0) or (len(msg['targets']) == 0):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        name = deviceID + '_' + deviceType
        dataTime = unixMilliseconds2Datetime(msg['targets'][0]['timestamp'])
        print('latest receiving time:', datetime.now(),
              ' dataTime: ', dataTime, name, end='\r')   # 持续显示
        # 当前消息的设备
        if name not in controllerGroup:
            logger.error('该设备未在config中设置, 请添加.' + name)
            continue
        # log文件保存更新
        controllerGroup[name].logger.updateDayLogFile()
        # 算法检测
        msg, events = controllerGroup[name].run(msg)
        if (events is None) or (len(events) == 0):
            continue    # 未检测到事件
        # 上报事件
        hp.run(events)


if __name__ == "__main__":
    # simulatedMain()
    main()
    # evaluateDeployedModel()
    # mainGrouped()

    # total evaluation
    # dataPath = r'D:\东南大学\科研\金科\data\dataRy\data\2024-3-26-8.txt'
    # dataPath = r'D:\东南大学\科研\金科\data\dataRy\data\2024-3-26-9.txt'
    # dataPath = r'D:\东南大学\科研\金科\data\dataRy\data\2024-3-27-17.txt'
    # dataPath = r'D:\东南大学\科研\金科\data\dataRy\data\2024-3-27-18.txt'
    # simulatedMainGrouped(dataPath)
