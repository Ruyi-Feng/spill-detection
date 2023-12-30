from rsu_simulator import Smltor
from message_driver import Driver
from road_calibration import Calibrator
import yaml


# 通过
def test_calibrator():
    '''test function calibrator

    测试标定器。

    测试方法:
    1. 生成标定器
    2. 生成仿真器
    3. 仿真器读取数据
    4. 标定器接受数据
    5. 标定器标定
    6. 标定器保存
    '''

    # 读取配置文件
    configPath = './config.yml'
    with open(configPath, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # 生成标定器
    clbPath = './road_calibration/clb.yml'
    calibrator = Calibrator(clbPath,
                            fps=config['fps'],
                            laneWidth=config['calib']['lane_width'],
                            emgcWidth=config['calib']['emgc_width'],
                            cellLen=config['calib']['cell_len'],
                            qMerge=config['calib']['q_merge'])

    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver()

    # 仿真器读取数据
    while True:
        msg = smltor.run()
        if msg == '':
            break
        valid, msg = d.receive(msg)
        if not valid:
            continue
        # 标定器接受数据
        calibrator.run(msg)

    # 标定器标定
    calibrator.calibrate()

    # 标定器保存
    clb = calibrator.save()

    # 判定
    standardClb = {
        1:
        {
            'emgc': True, 'vDir': {'x': 1, 'y': -1},
            'start': 799.3, 'len': 799.3, 'end': 0,
            'coef': [-0.907, -45.799, 180.391],
            'cells': [False, False, False, False, False, False, False, False,
                      False, False, False, False, True, True, True, True]
        },
        2:
        {
            'emgc': False, 'vDir': {'x': 1, 'y': -1},
            'start': 799.3, 'len': 799.3, 'end': 0,
            'coef': [-0.907, -45.799, 197.175],
            'cells': [False, False, False, False, True, True, True, True,
                      True, True, True, True, True, True, True, True]
        },
        3:
        {
            'emgc': False, 'vDir': {'x': 1, 'y': -1},
            'start': 799.3, 'len': 799.3, 'end': 0,
            'coef': [-0.907, -35.443, 340.721],
            'cells': [False, False, False, True, True, True, True, True,
                      True, True, True, True, True, True, True, True]
        },
        4:
        {
            'emgc': False, 'vDir': {'x': 1, 'y': -1},
            'start': 799.3, 'len': 799.3, 'end': 0,
            'coef': [-0.907, -32.508, 469.615],
            'cells': [False, False, False, False, False, True, True, True,
                      True, True, True, True, True, True, True, True]
        },
        5:
        {
            'emgc': False, 'vDir': {'x': -1, 'y': 1},
            'start': 0, 'len': 799.3, 'end': 799.3,
            'coef': [-0.907, -17.134, 715.163],
            'cells': [False, True, True, True, True, True, True, True,
                      True, True, True, True, True, True, True, True]
        },
        6:
        {
            'emgc': False, 'vDir': {'x': -1, 'y': 1},
            'start': 0, 'len': 799.3, 'end': 799.3,
            'coef': [-0.907, -12.016, 762.724],
            'cells': [False, True, True, True, True, True, True, True,
                      True, True, True, True, True, True, True, True]
        },
        7:
        {
            'emgc': False, 'vDir': {'x': -1, 'y': 1},
            'start': 0, 'len': 799.3, 'end': 799.3,
            'coef': [-0.907, -4.521, 786.292],
            'cells': [False, True, True, True, True, True, True, True,
                      True, True, True, True, True, True, True, True]},
        8:
        {
            'emgc': True, 'vDir': {'x': -1, 'y': 1},
            'start': 0, 'len': 799.3, 'end': 799.3,
            'coef': [-0.907, -4.521, 803.075],
            'cells': [False, False, True, False, False, False, True, False,
                      True, True, True, False, True, True, True, True]
        }
    }
    assert clb == standardClb


if __name__ == '__main__':
    test_calibrator()
