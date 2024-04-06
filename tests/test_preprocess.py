from rsu_simulator import Smltor
from message_driver import Driver
from pre_processing import PreProcessor
import yaml
from pre_processing.utils import carsList2Dict

def test_preprocess():
    # 1. 离线数据测试
    # 读取配置文件
    cfgPath = './config.yml'
    with open(cfgPath, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    # 读取标定文件
    clbPath = './road_calibration/clbymls/clb_K68+366_1.yml'
    with open(clbPath, 'r') as f:
        clb = yaml.load(f, Loader=yaml.FullLoader)
    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver(cfg['fps'])
    # 生成预处理器
    pp = PreProcessor(cfg, clb)
    # 仿真器读取数据
    while True:
        msg = smltor.run()
        if msg == '':
            break
        valid, cars = d.receive(msg)
        if not valid:
            continue
        # 预处理接收数据
        cars = pp.run(cars)
        # 检查点1
        # 预处理后的数据为列表
        assert type(cars) == list

    # 2. 备用数据测试
    # 断续轨迹补全平滑测试数据, 备用
    # print('you passed test of preprocess.py! A number is generated to you:',
    #       dataDiscontinuous[0]['XDecx'])
    # for car in dataDiscontinuous:
    #     cars = [car]   # 模拟传输来的1条信息
    #     valid, cars = d.run(cars)
    #     assert valid == True
    #     cars = tm.run(cars)
    #     assert type(cars) == list


def test_VandAccCalculator():
    # 配置
    cfgPath = './config.yml'
    with open(cfgPath, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    # 标定
    clbPath = './road_calibration/clbymls/clb_K68+366_1.yml'
    with open(clbPath, 'r') as f:
        clb = yaml.load(f, Loader=yaml.FullLoader)

    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver(20)
    # 预处理器
    pp = PreProcessor(cfg, clb)
    # 仿真器读取数据
    while True:
        msg = smltor.run()
        if msg == '':
            break
        valid, cars = d.receive(msg)
        if not valid:
            continue
        # 计算速度、全局速度和加速度属性
        pp._updateLatestTimestamp(cars)
        cars = carsList2Dict(cars)
        pp._updateRecords(cars)
        cars = pp.vaCal.run(pp.records, cars)
        # 检查点1
        # 经过计算后的数据中存在speed, globalSpeed, ax, ay, a属性
        for car in cars.values():
            assert 'speed' in car
            assert 'globalSpeed' in car
            assert 'ax' in car
            assert 'ay' in car
            assert 'a' in car
    print('you passed test of VandAccCalculator!')


if __name__ == "__main__":
    test_preprocess()
    # test_VandAccCalculator()
