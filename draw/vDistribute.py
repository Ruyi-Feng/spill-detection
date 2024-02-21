import matplotlib.pyplot as plt
import pandas as pd


'''Draw the distribution of vx and vy, as well as scatter plot of x and y.'''


filePath = './data/result.csv'


def drawVxVy():
    # 列名为VDecVx，VDecVy
    data = pd.read_csv(filePath)
    # 画图
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    # 画速度分布, 直方图分布间隔为1, 相邻柱子不完全相邻
    data['VDecVx'].plot(kind='hist', ax=ax[0, 0], title='Vx distribution',
                        bins=range(-4, 4, 1))
    data['VDecVy'].plot(kind='hist', ax=ax[0, 1], title='Vy distribution',
                        bins=range(-50, 50, 1))
    # 画散点图, 散点大小为0.5
    data.plot(kind='scatter', x='VDecVx', y='VDecVy', ax=ax[1, 0],
              title='Vx-Vy scatter plot', s=0.5)
    data.plot(kind='scatter', x='XDecx', y='YDecy', ax=ax[1, 1],
              title='X-Y scatter plot', s=0.5)
    # data.plot(kind='scatter', x='VDecVx', y='VDecVy', ax=ax[1, 0],
    #           title='Vx-Vy scatter plot')
    # data.plot(kind='scatter', x='XDecx', y='YDecy', ax=ax[1, 1],
    #           title='X-Y scatter plot')
    # 保存图片
    plt.savefig('./draw/vxvy.png')


if __name__ == '__main__':
    drawVxVy()
