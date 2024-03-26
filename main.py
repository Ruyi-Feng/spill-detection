import os
import sys
import argparse
import json
from datetime import datetime
from controller import Controller
from kafka import KafkaConsumer
from connector import HttpPoster
from rsu_simulator import Smltor
from logger import MyLogger
from utils import loadConfig, isNotTargetDevice, isInvalidMsg
from utils import checkConfigDevices, argsFromDeviceID


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
    args = params()
    logger = MyLogger(args.deviceId, args.deviceType)
    controller = Controller(configPath, clbPath, logger, args)
    smltor = Smltor(dataPath)

    # 模拟接受数据
    while True:
        msg = smltor.run()
        if msg == '':   # 读取到文件末尾
            break
        msg, events = controller.run(msg)  # msg为控制器返回的需要发送的数据


def main():
    args = params()
    logger = MyLogger(args.deviceId, args.deviceType)
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    # 生成kafka消费者
    kc = KafkaConsumer(
        cfg['topic'], bootstrap_servers=cfg['ip'],
        api_version=tuple(cfg['producerversion']),
        group_id=cfg['groupid'],
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
        print('latest receiving time:', datetime.now(), end='\r')   # 持续显示
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        # 非空数据判断
        if isInvalidMsg(msg) or isNotTargetDevice(msg, args):
            continue
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
                                           logger4Device, args)
    print('算法组件生成成功, 数据进入算法通道.')
    # 持续性运行接收
    # 模拟接受数据
    while True:
        msg = smltor.run()
        if msg == '':   # 读取到文件末尾
            break
        # 非空数据判断
        if isInvalidMsg(msg):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        name = deviceID + '_' + deviceType
        # dataTime = unixMilliseconds2Datetime(msg['targets'][0]['timestamp'])
        # print('latest receiving time:', datetime.now(),
        #       ' dataTime: ', dataTime, name, end='\r')   # 持续显示

        # 当前消息的设备
        if name not in controllerGroup:
            print('该设备未在config中设置, 请添加.' + name)
            continue
        # log文件保存更新
        controllerGroup[name].logger.updateDayLogFile()
        # 算法检测
        msg, events = controllerGroup[name].run(msg)


def evaluateDeployedModel():
    '''function evaluateDeployedModel

    读取从部署地点的实时保存数据文件,
    模拟实时接收数据, 检验事件结果,
    评估部署模型的性能。
    '''
    # dataDir = './data/'
    dataDir = r'D:\东南大学\科研\金科\data'
    # 2024-3-26-0.txt, 568914行
    # 2024-3-26-1.txt, 863957行
    for file in os.listdir(dataDir):
        if ('dump' in file) or ('result' in file) or ('heartbeat' in file):
            continue
        print(file, 'is running.')
        simulatedMainGrouped(dataDir + '/' + file)


def mainGrouped():
    '''多设备组合的主函数'''
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
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        name = deviceID + '_' + deviceType
        print('latest receiving time:', datetime.now(), name, end='\r')
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
    # main()
    evaluateDeployedModel()
    # mainGrouped()
