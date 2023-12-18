from rsu_simulator import Smltor
from calibration import Calibrator


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

    # 生成标定器
    clbPath = './calibration/clb.yml'
    calibrator = Calibrator(clbPath)

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

    return traffic


if __name__ == '__main__':
    traffic = test_calibrator()
    assert type(traffic) == dict
