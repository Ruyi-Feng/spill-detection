import json
from controller import Controller


if __name__ == "__main__":
    configPath = './config.yml'
    clbPath = './calibration/clb.yml'
    dataPath = './data/result.txt'

    # 应在主代码开头生成控制器
    controller = Controller(configPath, clbPath)

    # 模拟接受数据
    with open(dataPath) as f:
        for msg in f.readlines():
            # 接受数据
            try:
                msg = json.loads(msg)  # 接收到list数据
            except AttributeError:
                pass    # 非检测信息则会接收到str数据

            msg, traffic, event = controller.receive(msg)  # msg为控制器返回的需要发送的数据
