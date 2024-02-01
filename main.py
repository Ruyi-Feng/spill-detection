from controller import Controller
from connector import KafkaConsumer, HttpPoster
from rsu_simulator import Smltor
from utils import loadConfig

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
    kc = KafkaConsumer(cfg['kafka']['ip'],
                       cfg['kafka']['topic'],
                       cfg['kafka']['groupid'],
                       cfg['kafka']['key'])
    # 生成http上报器
    hp = HttpPoster(cfg['http']['url'])

    # 接收
    while True:
        # 持续性运行接收
        msg = kc.run()
        if (msg is None) or (msg == '') or (not msg):
            continue     # 接收到空数据
        # 算法检测
        msg, events = controller.run(msg)
        if len(events) == 0:
            continue    # 未检测到事件
        # 上报事件
        hp.run(events)


if __name__ == "__main__":
    # simulatedMain()
    main()
