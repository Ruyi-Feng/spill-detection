import yaml
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
    # 生成仿真器
    sm = Smltor(dataPath)
    # 生成路口管理器
    tm = TrafficMng(clb, config)
    # 开始运行
    OuterCount = 0      # tm内部count因重置为0的机制, 不能直接用来判定运行计数
    while True:
        msg = sm.run()
        if msg == '':
            break
        if type(msg) == str:
            continue
        OuterCount += 1
        tm.update(msg)
        # 检查点1
        # 检验是否成功计算路段流量Q
        if OuterCount >= tm.itv:
            assert tm.Q > 0
        else:
            assert tm.Q == 0


if __name__ == '__main__':
    testManager()
