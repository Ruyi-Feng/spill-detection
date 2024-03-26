import sys
import argparse
import json
from datetime import datetime
from controller import Controller
from kafka import KafkaConsumer
from connector import HttpPoster
from rsu_simulator import Smltor
from utils import loadConfig, isNotTargetDevice, isInvalidMsg
from logger import MyLogger
from utils import argsFromDeviceID

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
        logger.info('接收该设备数据: deviceID:' + deviceID +\
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


def mainGrouped():
    '''多设备组合的主函数'''
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    deviceNum1, deviceNum2 = len(cfg['deviceIDs']), len(cfg['deviceTypes'])
    if deviceNum1 != deviceNum2:
        logger.error('设备ID与设备类型数量不匹配. 请检查config.yml')
        return
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
    logger = MyLogger('main', 'noDeivce')
    logger.info('kafka与http数据通信组件已生成.')

    # # 获取当前设备信息
    logger.info('waiting the first message to obtain device information...')
    # for msgBytes in kc:     # 从kafka接收一帧数据以确定当前设备的信息
    #     msgStr = msgBytes.value.decode('utf-8')
    #     msg = json.loads(msgStr)        # dict
    #     if isInvalidMsg(msg) or isNotTargetDevice(msg, args):
    #         continue
    #     deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
    #     logger.info('接收该设备数据: deviceID:' + deviceID +\
    #                 'deviceType:' + deviceType)
    #     break

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
        print('latest receiving time:', datetime.now(), end='\r')   # 持续显示
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        # 非空数据判断
        if isInvalidMsg(msg):
            continue
        # 当前消息的设备
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        name = deviceID + '_' + deviceType
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
    mainGrouped()
