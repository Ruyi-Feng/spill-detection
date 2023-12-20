import matplotlib.pyplot as plt
import numpy as np
from numpy import array
import pandas as pd


def drawLanes():
    # 轨迹数据
    data = pd.read_csv("./data/result.csv")
    xIndex = 1
    yIndex = 2
    laneIndex = 13
    colX = data.columns[xIndex]
    colY = data.columns[yIndex]
    colLane = data.columns[laneIndex]
    # data的colLane列， 10X车道直接改成X车道轨迹
    data[colLane] = data[colLane].apply(lambda x: x - 100 if x > 100 else x)

    # 车道数据
    lanePoly = {7: array([-1.02600506e+00,  5.91982461e-01,  7.29109709e+02]), 2: array([ -1.02600506, -43.61854953, 190.44435205]), 3: array([ -1.02600506, -36.37711312, 336.98972486]), 4: array([ -1.02600506, -27.93229522, 437.64531633]), 5: array([ -1.02600506, -12.10844453, 648.69092686]), 6: array([ -1.02600506,  -7.25923551, 720.14807315]), 1: array([ -1.02600506, -43.61854953, 186.2317913 ]), 8: array([-1.02600506e+00,  5.91982461e-01,  7.33322270e+02])}

    # 画图
    plt.figure(figsize=(16, 16))
    # 标注雷达原点
    plt.scatter([0], [0], s=100, c="red", marker="o")
    # 画轨迹
    for group, df_group in data.groupby(colLane):
        # 加alpha会变糊
        plt.scatter(df_group[colX], df_group[colY], label=group, s=1, alpha=0.2)
    # 画车道
    # lanePoly为每个laneID对应的二次拟合函数，系数为a*x^2+b*x+c
    # 每个车道中心线在一定范围的x内进行采样画图
    xmin, xmax = min(data[colX]), max(data[colX])
    ymin, ymax = min(data[colY]), max(data[colY])
    # xmin, xmax = min(data[colX]), 50
    xArr = np.linspace(xmin, xmax, 100)
    for laneID in lanePoly:
        yArr = lanePoly[laneID][0] * xArr * xArr + \
        lanePoly[laneID][1] * xArr + lanePoly[laneID][2]
        plt.plot(xArr, yArr, label='lane'+str(laneID), marker='*')

    # 添加元素
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    plt.ylim(ymin-100, ymax+100)
    plt.title("Trajectory")
    plt.legend(loc="best")
    plt.savefig("./trajectoryWithLane.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    drawLanes()