from controller import Controller

if __name__ == "__main__":
    configPath = './param.json'
    calibrationPath = './calibration/config.json'
    dataPath = './data/result.txt'
    
    # 应在主代码开头生成控制器
    controller = Controller(configPath, calibrationPath, dataPath)

    # 模拟接受数据
    with open(dataPath) as f:
        for data in f.readlines():
            # 接受数据
            msg, traffic, event = controller.receive(data)  # msg为控制器返回的需要发送的数据

