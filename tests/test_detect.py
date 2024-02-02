from rsu_simulator import Smltor
from message_driver import Driver
from event_detection import EventDetector
from pre_processing import PreProcessor
from utils import loadConfig, loadYaml
from tests.test_data.eventData import (dataSpill, dataSpillEvent,
                                       dataStop, dataStopEvent,
                                       dataLowSpeed, dataLowSpeedEvent,
                                       dataHighSpeed, dataHighSpeedEvent,
                                       dataIllegalOccupation,
                                       dataIllegalOccupationEvent,
                                       dataEmgcBrake, dataEmgcBrakeEvent,
                                       dataIncident, dataIncidentEvent,
                                       dataCrowdEvent)


# 读取配置文件
configPath = './config.yml'
cfg = loadConfig(configPath)
# 读取标定文件
calibPath = './road_calibration/clb.yml'
clb = loadYaml(calibPath)


def testDetect():
    '''离线数据测试'''
    print('-------离线数据测试-------')
    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver(cfg['fps'])
    # 生成预处理器
    pp = PreProcessor(cfg['maxCompleteTime'], cfg['smoothAlpha'])
    # 生成检测器(内含交通管理器)
    ed = EventDetector(clb, cfg)
    # 仿真器读取数据
    while True:
        msg = smltor.run()
        if msg == '':
            break
        valid, cars = d.receive(msg)
        if not valid:
            continue
        # 数据预处理
        cars = pp.run(cars)
        # 事件检测
        events = ed.run(cars)
        # 检查点1
        # 数据事件类型为list
        assert type(events) == dict


def testSpill():
    print('-------抛洒物检测测试-------')
    # 生成检测器(内含交通管理器)
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['spill']

    del dataSpillEvent['danger']
    del dataSpillEvent['eventID']
    # 迭代dataSpill检测
    for frame in dataSpill:
        events = ed.run(frame)
        # 非spill类的events应为False
        # 当spill为True时, events应为dataSpillEvent
        for type in events:
            if type != 'spill':
                assert not events[type]['occured']
            elif events[type]['occured']:
                tmp = events[type]['items']
                tmp = tmp[list(tmp.keys())[0]]
                del tmp['danger']
                del tmp['eventID']
                assert tmp == dataSpillEvent


def testStop():
    print('-------停车检测测试-------')
    # 生成检测器
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['stop']
    # 迭代dataStop检测
    for frame in dataStop:
        events = ed.run(frame)
        # 非stop类的events应为False
        # 当stop为True时, events应为dataStopEvent
        for type in events:
            if type != 'stop':
                assert not events[type]['occured']
            elif events[type]['occured']:
                assert events[type] == dataStopEvent


def testLowSpeed():
    print('-------低速检测测试-------')
    # 生成检测器
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['lowSpeed']
    # 迭代dataLowSpeed检测
    for frame in dataLowSpeed:
        events = ed.run(frame)
        # 非lowSpeed类的events应为False
        for type in events:
            if type != 'lowSpeed':
                assert not events[type]['occured']
            elif events[type]['occured']:
                assert events[type] == dataLowSpeedEvent


def testHighSpeed():
    print('-------高速检测测试-------')
    # 生成检测器
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['highSpeed']
    # 迭代dataHighSpeed检测
    for frame in dataHighSpeed:
        events = ed.run(frame)
        # 非highSpeed类的events应为False
        for type in events:
            if type != 'highSpeed':
                assert not events[type]['occured']
            elif events[type]['occured']:
                assert events[type] == dataHighSpeedEvent


def testIllegalOccupation():
    print('-------非法占用应急车道检测测试-------')
    # 生成检测器
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['illegalOccupation']
    # 迭代dataIllegalOccupation检测
    for frame in dataIllegalOccupation:
        events = ed.run(frame)
        # 非illegalOccupation类的events应为False
        for type in events:
            if type != 'illegalOccupation':
                assert not events[type]['occured']
            elif events[type]['occured']:
                assert events[type] == dataIllegalOccupationEvent


def testEmgcBrake():
    print('-------紧急刹车检测测试-------')
    # 生成检测器
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['emgcBrake']
    # 迭代dataEmgcBrake检测
    for frame in dataEmgcBrake:
        events = ed.run(frame)
        # 非emgcBrake类的events应为False
        for type in events:
            if type != 'emgcBrake':
                assert not events[type]['occured']
            elif events[type]['occured']:
                assert events[type] == dataEmgcBrakeEvent


def testIncident():
    print('-------事件检测测试-------')
    # 生成检测器
    ed = EventDetector(clb, cfg)
    ed.eventTypes = ['incident']
    # 迭代dataIncident检测
    for frame in dataIncident:
        events = ed.run(frame)
        # 非incident类的events应为False
        for type in events:
            if type != 'incident':
                assert not events[type]['occured']
            elif events[type]['occured']:
                assert events[type] == dataIncidentEvent


def testCrowd():
    print('-------拥堵检测测试-------')
    # 生成检测器(内含交通管理器)
    ed = EventDetector(clb, cfg)
    ed.lanes[3].k = 30
    ed.lanes[3].v = 3
    cars = [{'id': 1, 'x': 0.1, 'y': 3.0, 'vx': 0.13, 'vy': 3.0, 'laneID': 3,
             'ay': 0, 'ax': 0, 'a': 0, 'timestamp': 200, 'speed': 3.0,
             'deviceID': 'K68+366', 'deviceType': '1'}]
    ed.eventTypes = ['crowd']
    events = ed.run(cars)
    for type in events:
        if type != 'crowd':
            assert not events[type]['occured']
        else:
            assert events[type] == dataCrowdEvent


if __name__ == "__main__":
    testDetect()
    # testSpill()
    # testStop()
    # testLowSpeed()
    # testHighSpeed()
    # testIllegalOccupation()
    # testEmgcBrake()
    # testIncident()
    # testCrowd()
