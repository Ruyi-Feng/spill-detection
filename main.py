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


if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = 'six.moves'


def params():
    parser = argparse.ArgumentParser(description='spill-detection parameters')
    parser.add_argument('--deviceId', type=str, help="K73+516")
    parser.add_argument('--deviceType', type=int, default=0,
                        help="radar 1, camera 2")
    args = parser.parse_args()
    return args


def simulatedMain():
    configPath = './config.yml'
    clbPath = './road_calibration/clb.yml'
    dataPath = './data/result.txt'

    controller = Controller(configPath, clbPath)
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
        # if len(msgStr) < 2:
        #     continue
        # if msgStr[1] == '\'':       # 避免传来的数据单引号不满足json格式
        #     msgStr = swapQuotes(msgStr)
        msg = json.loads(msgStr)        # dict
        if isInvalidMsg(msg) or isNotTargetDevice(msg, args):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        logger.info('接收该设备数据: deviceID:', deviceID, 'deviceType:', deviceType)
        break

    # 根据设备信息生成clbPath, 为./road_calibration/clb_设备名_设备类型.yml
    # 生成主控制器
    clbPath = './road_calibration/clbymls/clb_' + \
        deviceID + '_' + deviceType + '.yml'
    controller = Controller(configPath, clbPath, logger)
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
        # 算法检测
        msg, events = controller.run(msg)
        if (events is None) or (len(events) == 0):
            continue    # 未检测到事件
        # 上报事件
        hp.run(events)
        # logger.error(events)  # 在各个事件告警时计入日志


if __name__ == "__main__":
    # simulatedMain()
    main()
