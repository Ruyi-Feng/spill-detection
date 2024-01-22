# import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def laneChangePlot(data):
    # data各列为
    # TargetId,XDecx,YDecy,ZDecz,VDecVx,VDecVy,Xsize,Ysize,TargetType,Longitude,Latitude,Confidence,EventType,LineNum,Frame
    # 以frame为横轴, 以车辆id为纵轴, 画出各id车辆随frame增加, 其laneNum的变化。图中用不同颜色的色块表示不同的laneNum。
    # 画出的图形保存在draw文件夹中
    # TODO2
    # 以下为示例代码, 可删除

    return data


if __name__ == "__main__":
    data = pd.read_csv(Path(__file__).parents[1] / 'data' / 'result.csv')
    laneChangePlot(data)
