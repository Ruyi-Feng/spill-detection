import sys
import argparse
import json
from datetime import datetime
from controller import Controller
from kafka import KafkaConsumer
from connector import HttpPoster
from rsu_simulator import Smltor
from utils import loadConfig

if sys.version_info >=(3,12,0):
    sys.modules['kafka.vendor.six.moves'] = 'six.moves'

def params():
    parser = argparse.ArgumentParser(description='spill-detection parameters')
    parser.add_argument('--deviceId', type=str, help="K73+516")
    parser.add_argument('--deviceType', type=int, default=0, help="radar 1, camera 2")
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

def isNotTargetDevice(msg, args):
    if msg['deviceID'] != args.deviceId:
        return True
    return False

def main():
    # 读取配置文件
    configPath = './config.yml'
    cfg = loadConfig(configPath)
    args = params()
    # 生成kafka消费者
    kc = KafkaConsumer(cfg['topic'], bootstrap_servers=cfg['ip'],
                       api_version=tuple(cfg['producerversion']),
                    #    auto_offset_reset='smallest',
                       group_id=cfg['groupid'],
                       auto_commit_interval_ms=cfg['kafkaAutoCommitIntervalMs'])
    # 生成http上报器
    hp = HttpPoster(cfg['http'])
    print('数据通信组件生成成功')

    # 获取当前设备信息
    print('waiting the first message to obtain device information...')
    for msgBytes in kc:     # 从kafka接收一帧数据以确定当前设备的信息
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        if (msg is None) or (msg == '') or (not msg) or isNotTargetDevice(msg, args):
            continue
        deviceID, deviceType = msg['deviceID'], str(msg['deviceType'])
        print('deviceID:', deviceID, 'deviceType:', deviceType)
        break

    # 根据设备信息生成clbPath, 为./road_calibration/clb_设备名_设备类型.yml
    # 生成主控制器
    clbPath = './road_calibration/clbymls/clb_' + deviceID + '_' + deviceType + '.yml'
    controller = Controller(configPath, clbPath, args)
    print('算法组件生成成功, 开始接收数据')

    # 持续性运行接收
    for msgBytes in kc:
        # 数据解码
        print('receive time:', datetime.now(), end='\r')  # end='\r'
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        # 非空数据判断
        if (msg is None) or (msg == '') or (not msg):
            continue
        if isNotTargetDevice(msg, args):
            continue
        # 算法检测
        msg, events = controller.run(msg)
        if (events is None) or (len(events) == 0):
            continue    # 未检测到事件
        # 上报事件
        hp.run(events)
        print(events)


if __name__ == "__main__":
    # simulatedMain()
    main()
