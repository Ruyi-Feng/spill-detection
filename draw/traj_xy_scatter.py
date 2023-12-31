import pandas as pd
import matplotlib.pyplot as plt


def trajXYPlot():
    # 指定数据和列
    data = pd.read_csv("./data/result.csv")
    xIndex = 1
    yIndex = 2
    laneIndex = 13

    colX = data.columns[xIndex]
    colY = data.columns[yIndex]
    colLane = data.columns[laneIndex]

    # 画图
    plt.figure(figsize=(16, 16))
    plt.scatter([0], [0], s=100, c="red", marker="o")  # 标注雷达原点
    # plt.scatter(data[data.columns[xIndex]], data[data.columns[yIndex]], s=1)
    for group, dfLane in data.groupby(colLane):
        # 加alpha会变糊
        plt.scatter(dfLane[colX], dfLane[colY], label=group, s=1, alpha=0.5)

    # 添加元素
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    plt.title("Trajectory")
    plt.legend(loc="best")
    plt.savefig("./trajectory.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    trajXYPlot()
