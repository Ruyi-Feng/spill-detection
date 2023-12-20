import matplotlib.pyplot as plt
import numpy as np
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

    # 车道数据
    lanePoly = {1: np.array([-0.907055758, -4.51024210, 769.5545122]),
                2: np.array([ -0.90705576,  -4.5102421 , 245.42938442]),
                3: np.array([ -0.90705576,  -4.5102421 , 280.04165255]),
                4: np.array([ -0.90705576,  -4.5102421 , 282.55912225]),
                5: np.array([ -0.90705576,  -4.5102421 , 536.99610447]),
                6: np.array([ -0.90705576,  -4.5102421 , 666.7797432 ]),
                7: np.array([ -0.90705576,  -4.5102421 , 786.30118203]),
                8: np.array([-0.907055758, -4.51024210, 803.0478517])}

    # 画图
    plt.figure(figsize=(16, 16))
    # 标注雷达原点
    plt.scatter([0], [0], s=100, c="red", marker="o")
    # 画轨迹
    for group, df_group in data.groupby(colLane):
        # 加alpha会变糊
        plt.scatter(df_group[colX], df_group[colY], label=group, s=1, alpha=0.5)
    # 画车道
    # lanePoly为每个laneID对应的二次拟合函数，系数为a*x^2+b*x+c
    # 每个车道中心线在一定范围的x内进行采样画图
    xmin, xmax = min(data[colX]), max(data[colX])
    xArr = np.linspace(xmin, xmax, 100)
    for laneID in lanePoly:
        yArr = lanePoly[laneID][0] * xArr * xArr + \
        lanePoly[laneID][1] * xArr + lanePoly[laneID][2]
        plt.plot(xArr, yArr, label='lane'+str(laneID), marker='*')

    # 添加元素
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    plt.title("Trajectory")
    plt.legend(loc="best")
    plt.savefig("./trajectoryWithLane.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    drawLanes()