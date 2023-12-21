from traffic_manager import LaneMng


def testCarLocCell():
    l = LaneMng(1, False, 
                len=100, start=0, end=100, vdir=1, 
                coef={}, cellLen=10, clbCell={})
    car = {'YDecy': 5}
    order = 0
    o = l._carLocCell(car)
    assert o == order

    car = {'YDecy': 25}
    order = 2
    o = l._carLocCell(car)
    assert o == order

    car = {'YDecy': 95}
    order = 9
    o = l._carLocCell(car)
    assert o == order

    car = {'YDecy': 100}
    order = 10
    o = l._carLocCell(car)
    assert o == order

    l = LaneMng(1, False, 
                len=100, start=100, end=0, vdir=-1, 
                coef={}, cellLen=10, clbCell={})
    car = {'YDecy': 5}
    order = 9
    o = l._carLocCell(car)
    assert o == order

    car = {'YDecy': 25}
    order = 7
    o = l._carLocCell(car)
    assert o == order

    car = {'YDecy': 95}
    order = 0
    o = l._carLocCell(car)
    assert o == order

    car = {'YDecy': 100}
    order = 0
    o = l._carLocCell(car)
    assert o == order


if __name__ == "__main__":
    testCarLocCell()
    print('all passed')
