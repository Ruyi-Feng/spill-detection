from traffic_manager import LaneMng
import yaml


def testCarLocCell():
    cfgPath = 'config.yml'
    with open(cfgPath, 'r', encoding='utf-8') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    lm = LaneMng(1, False,
                 len=100, start=0, end=100, vdir=1,
                 coef={}, cellLen=10, cellsValid=[True]*10,
                 cfg=cfg, cacheRet=50)
    car = {'y': 5}
    order = 0
    o = lm._carLocCell(car)
    assert o == order

    car = {'y': 25}
    order = 2
    o = lm._carLocCell(car)
    assert o == order

    car = {'y': 95}
    order = 9
    o = lm._carLocCell(car)
    assert o == order

    car = {'y': 100}
    order = 10
    o = lm._carLocCell(car)
    assert o == order

    lm = LaneMng(1, False,
                 len=100, start=100, end=0, vdir=-1,
                 coef={}, cellLen=10, cellsValid=[True]*10,
                 cfg=cfg, cacheRet=50)
    car = {'y': 5}
    order = 9
    o = lm._carLocCell(car)
    assert o == order

    car = {'y': 25}
    order = 7
    o = lm._carLocCell(car)
    assert o == order

    car = {'y': 95}
    order = 0
    o = lm._carLocCell(car)
    assert o == order

    car = {'y': 100}
    order = 0
    o = lm._carLocCell(car)
    assert o == order


if __name__ == "__main__":
    testCarLocCell()
    print('all passed')
