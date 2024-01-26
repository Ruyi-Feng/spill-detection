from rsu_simulator import Smltor
from message_driver import Driver
from road_calibration import Calibrator
import yaml
from tests.test_data.standardClb import standardClb


# 通过
def test_calibrator():
    '''test function calibrator

    测试标定器。
    '''
    # 读取配置文件
    cfgPath = './config.yml'
    with open(cfgPath, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    # 生成标定器
    clbPath = './road_calibration/clb.yml'
    calibrator = Calibrator(clbPath,
                            fps=cfg['fps'],
                            laneWidth=cfg['laneWidth'],
                            emgcWidth=cfg['emgcWidth'],
                            cellLen=cfg['cellLen'],
                            qMerge=cfg['qMerge'])

    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver(cfg['fps'])

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

    # 检查点1
    # 标定器标定结果与标准结果相同
    assert clb == standardClb


if __name__ == '__main__':
    test_calibrator()
