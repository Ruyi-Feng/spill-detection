from controller import Controller
from rsu_simulator import Smltor

if __name__ == "__main__":
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
