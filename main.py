import sys, json
from controller import Controller
from kafka import KafkaConsumer
from connector import HttpPoster
from rsu_simulator import Smltor
from utils import loadConfig


if sys.version_info > (3, 12, 0):       # for python version compatibility
    sys.modules['kafka.vendor.six.moves'] = 'six.moves'


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
    # 生成主控制器
    configPath = './config.yml'
    clbPath = './road_calibration/clb.yml'
    controller = Controller(configPath, clbPath)
    # 生成kafka消费者
    cfg = loadConfig(configPath)
    kc = KafkaConsumer(cfg['topic'], bootstrap_servers=cfg['ip'],
                       api_version=tuple(cfg['producerversion']),
                       group_id=cfg['groupid'])

    # 生成http上报器
    hp = HttpPoster(cfg['http'])

    # 持续性运行接收
    for msgBytes in kc:
        # 数据解码
        msgStr = msgBytes.value.decode('utf-8')
        msg = json.loads(msgStr)        # dict
        # 非空数据判断
        if (msg is None) or (msg == '') or (not msg):
            continue
        print('main: msg', type(msg), msg)
        # 算法检测
        msg, events = controller.run(msg)
        if len(events) == 0:
            continue    # 未检测到事件
        # 上报事件
        hp.run(events)


if __name__ == "__main__":
    # simulatedMain()
    main()
