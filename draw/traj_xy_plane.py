import yaml
import os
import numpy as np
from numpy import array
import pandas as pd
import matplotlib.pyplot as plt

'''画出xy平面上的轨迹数据散点和车道标定情况。'''


def plotXYPlane(csvPath: str,
                xIndex: int, yIndex: int, laneIndex: int,
                cfgPath: str = None, clbPath: str = None,
                savePath: str = None, ifPlotLane: bool = False):
    '''function plotXYPlane

    input
    -----
    csvPath: str, 轨迹数据路径
    xIndex: int, x坐标索引(csv文件中的列索引)
    yIndex: int, y坐标索引(csv文件中的列索引)
    laneIndex: int, 车道索引(csv文件中的列索引)
    cfgPath: str, 配置文件路径
    clbPath: str, 标定文件路径
    savePath: str, 保存路径
    ifPlotLane: bool, 是否画车道标定情况

    trajXYScatter()和drawLanes()的统一接口,
    画出xy平面上的轨迹数据散点和车道标定情况。
    '''
    if ifPlotLane:
        if cfgPath is None or clbPath is None:
            raise ValueError("cfgPath and clbPath must be specified.")
        drawLanes(csvPath, cfgPath, clbPath, xIndex, yIndex, laneIndex)
    else:
        trajXYScatter(csvPath, xIndex, yIndex, laneIndex, savePath)


def trajXYScatter(csvPath: str,
                  xIndex: int, yIndex: int, laneIndex: int,
                  savePath: str = None):
    '''function trajXYScatter

    input
    -----
    csvPath: str, 轨迹数据路径
    xIndex: int, x坐标索引(csv文件中的列索引)
    yIndex: int, y坐标索引(csv文件中的列索引)
    laneIndex: int, 车道索引(csv文件中的列索引)
    savePath: str, 保存路径

    画出xy平面上的轨迹数据散点。
    '''
    # 指定数据和列
    data = pd.read_csv(csvPath)
    colX, colY = data.columns[xIndex], data.columns[yIndex]
    colLane = data.columns[laneIndex]

    # 画图
    plt.figure(figsize=(16, 16))
    plt.scatter([0], [0], s=100, c="red", marker="o")  # 标注雷达原点
    # plt.scatter(data[data.columns[xIndex]], data[data.columns[yIndex]], s=1)
    for group, dfLane in data.groupby(colLane):
        # 加alpha会变糊
        plt.scatter(dfLane[colX], dfLane[colY], label=group, s=1, alpha=0.5)

    # 添加元素
    if savePath is None:
        savePath = csvPath.split('.')[0] + '.png'
    saveFileName = os.path.basename(savePath).split('.')[0]
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    plt.title(saveFileName)
    plt.legend(loc="best")
    plt.savefig(savePath, dpi=300)
    # plt.show()


def drawLanes(csvPath: str, cfgPath: str, clbPath: str,
              xIndex: int, yIndex: int, laneIndex: int,
              savePath: str = None):
    '''function drawLanes

    input
    -----
    csvPath: str, 轨迹数据路径
    cfgPath: str, 配置文件路径
    clbPath: str, 标定文件路径
    xIndex: int, x坐标索引(csv文件中的列索引)
    yIndex: int, y坐标索引(csv文件中的列索引)
    laneIndex: int, 车道索引(csv文件中的列索引)

    画出轨迹数据和车道标定情况。
    '''
    # 轨迹数据
    traj = pd.read_csv(csvPath)
    colX, colY = traj.columns[xIndex], traj.columns[yIndex]
    colLane = traj.columns[laneIndex]
    # traj的colLane列,  10X车道直接改成X车道轨迹
    traj[colLane] = traj[colLane].apply(lambda x: x - 100 if x > 100 else x)

    # 读取配置文件
    with open(cfgPath, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    cellLen = config['cellLen']
    # 读取标定文件
    with open(clbPath, 'r') as f:
        clb = yaml.load(f, Loader=yaml.FullLoader)
    # 获取标定信息
    start, end = clb[1]['start'], clb[1]['end']
    if start > end:
        start, end = end, start
    lanePoly = dict()
    vDir = dict()
    for laneID in clb:
        lanePoly[laneID] = array(clb[laneID]['coef'])
        vDir[laneID] = clb[laneID]['vDir']['y']
    colormap = ['brown', 'olive', 'gold', 'lime', 'red',
                'aqua', 'maroon', 'fuchsia', 'navy', 'silver',
                'teal']

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
    # lanePoly为每个laneID对应的二次拟合函数, 系数为a*x^2+b*x+c
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
        s, e, step = len(yArr)-1, 0, -vDir[laneID]  # step与vDir相反因为画图的顺序
        if step == 1:
            s, e = e, s
        for i in range(s, e, step):
            if (yArr[i] >= ymin) & (yArr[i] <= ymax):   # 仅画出边界内的, 要不不好看
                plt.annotate('', xy=(xArr[i+step], yArr[i+step]),
                             xytext=(xArr[i], yArr[i]),
                             arrowprops=dict(
                                facecolor=colormap[laneID],
                                shrink=0.05))
    # 绘制元胞
    end = (end // cellLen + 1) * cellLen
    for i in range(int(start), int(end) + cellLen, cellLen):
        plt.plot([xmin, xmax], [i, i], c='black', linewidth=0.5)

    # 添加元素
    if savePath is None:
        savePath = csvPath.split('.')[0] + '_withLane.png'
    saveFileName = os.path.basename(csvPath).split('.')[0]
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    plt.ylim(ymin-100, ymax+100)
    plt.title(saveFileName)
    plt.legend(loc="best")
    plt.savefig(savePath, dpi=300)
    # plt.show()


def extractColor(colormap, color_index):
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
    # 最初的result
    # xIndex = 1
    # yIndex = 2
    # laneIndex = 13
    # field data
    xIndex = 3
    yIndex = 4
    laneIndex = 2
    proDir = r"D:\myscripts\spill-detection"
    cfgPath = os.path.join(proDir, "config.yml")
    # # 画单个文件
    # csvPath = r"D:\myscripts\spill-detection\data\extractedData\2024-3-27-17_byDevice\K78+760_1.csv"
    # clbPath = os.path.join(proDir, "road_calibration/clbymls/clb_K78+760_1.yml")
    # 直接画整个文件夹下的所有csv文件
    
    # csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-3-26-8_byDevice"
    # 22日13，14，15，16，17时
    # 23日8，9时
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-22-13_byDevice"
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-22-14_byDevice"
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-22-15_byDevice"
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-22-16_byDevice"
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-22-17_byDevice"
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-23-8_byDevice"
    csvFileDir = r"D:\myscripts\spill-detection\data\extractedData\2024-4-23-9_byDevice"

    csvFiles = [x for x in os.listdir(csvFileDir) if x.endswith(".csv")]
    csvFileDict = {x.split(".")[0].split("_")[0]: x for x in csvFiles}
    clbFileDir = os.path.join(proDir, "road_calibration/clbymls")
    clbFiles = [x for x in os.listdir(clbFileDir) if (x.endswith(".yml")) and ('K' in x)]
    clbFileDict = {x.split(".")[0].split("_")[1]: x for x in clbFiles}
    for key in csvFileDict:
        if key not in clbFileDict:
            print(f'{key} calibration file not found.')
            continue
        csvPath = os.path.join(csvFileDir, csvFileDict[key])
        clbPath = os.path.join(clbFileDir, clbFileDict[key])
        if os.path.exists(key + '_1.png'):
            print(f'{key} without lane image already exists.')
            continue
        # plotXYPlane(csvPath, xIndex, yIndex, laneIndex,
        #             cfgPath, clbPath, ifPlotLane=True)
        if os.path.exists(key + '_1_withLane.png'):
            print(f'{key} with lane image already exists.')
            continue
        plotXYPlane(csvPath, xIndex, yIndex, laneIndex,
                    cfgPath, clbPath, ifPlotLane=False)
