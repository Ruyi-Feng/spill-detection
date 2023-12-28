import yaml
from message_driver import Driver
from rsu_simulator import Smltor
from traffic_manager import TrafficMng


# 通过
def testManager():
    configPath = './config.yml'
    clbPath = './road_calibration/clb.yml'
    dataPath = './data/result.txt'

    # 读取配置文件和标定文件
    with open(configPath, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    with open(clbPath, 'r') as f:
        clb = yaml.load(f, Loader=yaml.FullLoader)

    # 检查点1
    # 生成驱动器
    dr = Driver()
    # 生成仿真器
    sm = Smltor(dataPath)
    # 生成交通管理器
    tm = TrafficMng(clb, config)
    # 开始运行
    while True:
        msg = sm.run()
        if msg == '':
            break
        if type(msg) == str:
            continue
        # 交通管理器接受数据
        tm.update(msg)

    assert 0 == 0
