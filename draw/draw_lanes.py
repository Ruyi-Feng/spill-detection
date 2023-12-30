import matplotlib.pyplot as plt
import numpy as np
from numpy import array
import pandas as pd
import yaml


def drawLanes():
    # 轨迹数据
    traj = pd.read_csv("./data/result.csv")
    xIndex = 1
    yIndex = 2
    laneIndex = 13
    colX = traj.columns[xIndex]
    colY = traj.columns[yIndex]
    colLane = traj.columns[laneIndex]
    # traj的colLane列， 10X车道直接改成X车道轨迹
    traj[colLane] = traj[colLane].apply(lambda x: x - 100 if x > 100 else x)

    # 车道数据
    # lanePoly = {1: array([ -0.9070356 , -45.79906234, 180.3907908 ]),
    #             2: array([ -0.9070356 , -45.79906234, 197.17463419]),
    #             3: array([ -0.9070356 , -35.44343418, 340.72063149]),
    #             4: array([ -0.9070356 , -32.50765842, 469.61522482]),
    #             5: array([ -0.9070356 , -17.1337203 , 715.16259501]),
    #             6: array([ -0.9070356 , -12.01578466, 762.72382244]),
    #             7: array([ -0.9070356 ,  -4.52074536, 786.29154222]),
    #             8: array([ -0.9070356 ,  -4.52074536, 803.07538561])}
    # 不直接copy出lanePoly的值，从clb中读取
    clb = yaml.load(open("./road_calibration/clb.yml", 'r'), Loader=yaml.FullLoader)
    lanePoly = dict()
    vDir = dict()
    colormap = ['brown', 'olive', 'gold', 'lime', 'red', 'aqua', 'maroon', 'fuchsia', 'navy', 'silver']
    for laneID in clb:
        lanePoly[laneID] = array(clb[laneID]['coef'])
        vDir[laneID] = clb[laneID]['vDir']['y']

    # 画布生成
    plt.figure(figsize=(16, 16))
    # 雷达原点
    plt.scatter([0], [0], s=100, c="red", marker="o")
    # 绘制轨迹
    for group, dfLane in traj.groupby(colLane):
        # 加alpha会变糊
        if group < 100:
            plt.scatter(dfLane[colX], dfLane[colY],
                        label=group, c=colormap[group], s=1, alpha=0.2)
        else:   # 大于100的车道采用默认颜色
            plt.scatter(dfLane[colX], dfLane[colY],
                        label=group, s=1, alpha=0.2)
    # 绘制车道
    # lanePoly为每个laneID对应的二次拟合函数，系数为a*x^2+b*x+c
    # 每个车道中心线在一定范围的x内进行采样画图
    xmin, xmax = min(traj[colX]), max(traj[colX])
    ymin, ymax = min(traj[colY]), max(traj[colY])
    xArr = np.linspace(xmin, xmax, 50)
    for laneID in lanePoly:
        # 计算y值
        yArr = lanePoly[laneID][0] * xArr * xArr + \
            lanePoly[laneID][1] * xArr + lanePoly[laneID][2]
        # 绘制车道线
        plt.plot(xArr, yArr,
                 label='lane'+str(laneID), c=colormap[laneID], marker='o')
        # 绘制车道方向
        start, end, step = len(yArr)-1, 0, vDir[laneID]  # step与vDir相反因为画图的顺序
        if step == 1:
            start, end = end, start
        for i in range(start, end, step):
            if (yArr[i] >= ymin) & (yArr[i] <= ymax):   # 仅画出边界内的，要不不好看
                plt.annotate('', xy=(xArr[i+step], yArr[i+step]),
                             xytext=(xArr[i], yArr[i]),
                            arrowprops=dict(
                                facecolor=colormap[laneID],
                                shrink=0.05)
                            )

    # 添加元素
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    plt.ylim(ymin-100, ymax+100)
    plt.title("Trajectory")
    plt.legend(loc="best")
    plt.savefig("./trajectoryWithLane.png", dpi=300)
    plt.show()


def extract_color(colormap, color_index):
    '''
    input
    ------
    colormap: str, 色系名称
    color_index: int, 颜色索引

    output
    ------
    color: tuple, 颜色
    '''
    cmap = plt.get_cmap(colormap)
    colors = cmap(range(cmap.N))
    return colors[color_index]


if __name__ == '__main__':
    drawLanes()
