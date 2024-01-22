from event_detection import EventDetector
import yaml
from message_driver import Driver
from rsu_simulator import Smltor


def testDetect():
    '''离线数据测试'''
    # 读取配置文件
    configPath = './config.yml'
    with open(configPath, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # 读取标定文件
    calibPath = './road_calibration/clb.yml'
    with open(calibPath, 'r') as f:
        clb = yaml.load(f, Loader=yaml.FullLoader)
    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver()
    # 生成检测器(内含交通管理器)
    ed = EventDetector(clb, config)

    # 仿真器读取数据
    while True:
        msg = smltor.run()
        if msg == '':
            break
        valid, cars = d.receive(msg)
        if not valid:
            continue
        # 事件检测
        events = ed.run(cars)
        # 检查点1
        # 数据事件类型为list
        assert type(events) == dict


def testSpill():
    pass


def testStop():
    pass


def testLowSpeed():
    pass


def testHighSpeed():
    pass


def testIllegalOccupation():
    pass


def testEmgcBrake():
    pass


def testIncident():
    pass


def testCrowd():
    pass


if __name__ == "__main__":
    testDetect()
    testSpill()
    testStop()
    testLowSpeed()
    testHighSpeed()
    testIllegalOccupation()
    testEmgcBrake()
    testIncident()
    testCrowd()
