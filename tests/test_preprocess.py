from rsu_simulator import Smltor
from message_driver import Driver
from pre_processing import PreProcessor
import yaml


def test_preprocess():
    # 1. 离线数据测试
    # 读取配置文件
    cfgPath = './config.yml'
    with open(cfgPath, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    # 生成仿真器
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 生成驱动器
    d = Driver()
    # 生成预处理器
    pp = PreProcessor(comMaxFrm=cfg['maxCompleteTime'],
                      smthA=cfg['smoothAlpha'])
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


if __name__ == "__main__":
    test_preprocess()
