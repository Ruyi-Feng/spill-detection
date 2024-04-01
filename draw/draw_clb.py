'''画出clb文件的车道标定情况'''

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import yaml
import os


def drawClb(clbPath: str):
    '''function drawClb

    input
    -----
    clbPath: str, clb文件路径

    画出clb文件的车道标定情况

    clb内容
    ------
    1:
        cells:
        - false
        - false
        - false
        - false
        - false
        - false
        - false
        - false
        - false
        - false
        - false
        - false
        - true
        - true
        - true
        - true
        coef:
        - -0.862
        - -45.739
        - 177.781
        emgc: true
        end: 0
        len: 799.3
        start: 799.3
        vDir:
            x: 1
            y: -1
    2:
    '''
    # 读取clb文件
    with open(clbPath, 'r', encoding='utf-8') as f:
        clb = yaml.load(f, Loader=yaml.FullLoader)
    lanes = list(clb.keys())
    cellLen = 50
    maxDistance = -1e6
    # 画图
    fig, ax = plt.subplots(figsize=(20, 16))
    # 在xy平面画出cell表格，横坐标lane，纵坐标length

    # 用不同颜色标注出cell是否valid，浅蓝色为valid，花灰色为invalid，标注legend
    for id, laneClb in clb.items():
        maxDistance = laneClb['len'] if laneClb['len'] > maxDistance \
            else maxDistance
        for i, cell in enumerate(laneClb['cells']):
            color = (0.4, 0.6, 1) if cell else (0.5, 0.5, 0.5)
            rect = patches.Rectangle(xy=(id - 0.5, i * cellLen),
                                     width=1, height=50, color=color)
            ax.add_patch(rect)

    # 在各个cell标注出所在车道的运动正方向
    plt.xlabel('lane')
    plt.xlim(0, len(lanes) + 1)
    plt.ylim(0, maxDistance)
    plt.ylabel('distance')
    plt.title(clbPath[:-4].split('/')[-1])
    # plt.show()
    plt.savefig(clbPath[:-4] + '.png', dpi=300)

    return


if __name__ == '''__main__''':
    # clbPath = './road_calibration/clbymls/clb.yml'
    # drawClb(clbPath)
    fileList = os.listdir('./road_calibration/clbymls')
    for file in fileList:
        if file.endswith('.yml'):
            clbPath = './road_calibration/clbymls/' + file
            drawClb(clbPath)
