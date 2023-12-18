import numpy as np
import math


def calQuartiles(points: list, range: float = 1) -> list:
    '''func calQuartiles

    input
    ----------
    points: list
        一组数据点的坐标, shape=(n, 2)
    range: float
        附近范围, 用于计算该范围内四分位点均值

    return
    ----------
    result: list
        一组数据点的四分位点, shape=(5, 2)

    计算一组数据点的四分位点, 采用四分位点附近范围内的点的均值。
    将用于车道线拟合。
    '''
    y_values = [point[1] for point in points]
    q0 = np.percentile(y_values, 0)
    q1 = np.percentile(y_values, 25)
    q2 = np.percentile(y_values, 50)
    q3 = np.percentile(y_values, 75)
    q4 = np.percentile(y_values, 100)

    result = []
    for q in [q0, q1, q2, q3, q4]:
        nearby_points = [p for p in points if abs(p[1] - q) <= range]
        avg_x = sum([point[0] for point in nearby_points]) / len(nearby_points)
        avg_y = sum([point[1] for point in nearby_points]) / len(nearby_points)
        result.append([avg_x, avg_y])

    return result


def dbi(xys: np.ndarray):
    '''func dbi

    input
    ----------
    xys: np.ndarray
        一组数据点的坐标, shape=(n, 2)

    return
    ----------
    dbi: float
        Davies-Bouldin指数, 为各点到中心距离的平均值开方

    计算Davies-Bouldin指数(DBI),
    给定单独一组数据点xy, 计算该组数据点在平面上的分散程度。

    '''
    # 计算数据点的中心
    center = np.mean(xys, axis=0)
    # 计算数据点到中心的距离
    dists = np.linalg.norm(xys - center, axis=1)
    # 计算数据点到中心距离的平均值
    avgDist = np.mean(dists)
    # 平均距离再开方
    dbi = math.sqrt(avgDist)
    return dbi


if __name__ == '__main__':
    # 测试calQuartiles
    points = [[i, i] for i in range(21, 0, -2)]
    q = calQuartiles(points)
    print(q)

    # 测试dbi
    xys = np.array([[1, 1], [2, 2], [3, 3]])
    d = dbi(xys)
    print(d)

    xys = np.array([[1, 1], [1, 1], [1, 1]])
    d = dbi(xys)
    print(d)
