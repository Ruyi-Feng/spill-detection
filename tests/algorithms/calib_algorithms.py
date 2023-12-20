# import matplotlib.pyplot as plt
import numpy as np
from road_calibration.algorithms import polyfit2, polyfit2A0


def test_polyfit2():
    # y = 2x^2 + 3x + 4
    # [[x,y]]形式样例数据
    a = [2, 3, 4]
    data = [[x, a[0] * x * x + a[1] * x + a[2]] for x in range(0, 9, 2)]
    data = np.array(data)
    # 二次多项式拟合
    polyA = polyfit2(data)
    assert all(([a[i] - polyA[i] < 1e-5 for i in range(len(a))]))


def test_polyfit2A0():
    # y = 2x^2 + 3x + 4
    # 给定系数[2, 3]
    # [[x,y]]形式样例数据
    a = [2, 3, 4]
    data = [[x, a[0] * x * x + a[1] * x + a[2]] for x in range(0, 9, 2)]
    data = np.array(data)
    a21 = [2, 3]
    # 固定系数的二次多项式拟合
    polyA = polyfit2A0(data, a21)
    assert all(([a[i] - polyA[i] < 1e-5 for i in range(len(a))]))


if __name__ == '__main__':
    test_polyfit2()
    test_polyfit2A0()
    print('ok')
