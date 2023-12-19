import pandas as pd
from rsu_simulator.dataloader import loadDataAsDict
from tqdm import tqdm


def dict2df(data: dict):
    '''
    将轨迹数据从txt中读取为dict, 并转化为dataframe存储下来。
    data为帧索引的目标list, list元素為代表目標信息的dict。
    '''
    df_all = pd.DataFrame()
    for frame in tqdm(data.keys()):
        df = pd.DataFrame(data[frame])
        df["Frame"] = frame     # 在df中对应补充帧数据
        df_all = pd.concat([df_all, df], axis=0)
    # 按照laneID，TargetId和Frame排序
    df_all.sort_values(by=["LineNum", "TargetId", "Frame"], inplace=True)
    return df_all


if __name__ == "__main__":
    data = loadDataAsDict("../data/result.txt")
    df = dict2df(data)
    df.to_csv("../data/result.csv", index=False)
