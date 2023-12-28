from rsu_simulator import Smltor
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

    # 仿真器读取数据
    while True:
        msg = smltor.run()
        if msg == '':
            break
        if type(msg) == str:    # 非目标信息
            continue

        # 标定器接受数据
        calibrator.recieve(msg)

    # 标定器标定
    calibrator.calibrate()

    # 标定器保存
    traffic = calibrator.save()

    assert type(traffic) == dict
