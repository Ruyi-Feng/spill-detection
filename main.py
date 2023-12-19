from controller import Controller
from rsu_simulator import Smltor

if __name__ == "__main__":
    configPath = './config.yml'
    clbPath = './calibration/clb.yml'
    dataPath = './data/result.txt'

    # 应在主代码开头生成控制器
    controller = Controller(configPath, clbPath)
    smltor = Smltor(dataPath)

    # 模拟接受数据
    while True:
        msg = smltor.run()
        if msg == '':   # 读取到文件末尾
            break

        msg, traffic, event = controller.receive(msg)  # msg为控制器返回的需要发送的数据
        print(msg[0])
