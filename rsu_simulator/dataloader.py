# -*-coding=utf-8-*-
import json

def load_data_by_line(path):
    '''
    按行加载读取轨迹txt数据
    txt数据格式：
    每行为一帧的目标，形式为list，其中元素为代表目标信息的dict。
    '''
    with open(path) as f:
        for line in f.readlines():
            # print(line)
            try:
                data = json.loads(line)
            except:
                pass


def load_data_all(path):
    '''
    加载txt数据，并保存到一个dict中.
    txt数据格式：
    每行为一帧的目标，形式为list，其中元素为代表目标信息的dict。
    返回的组织格式{frame:[]target}。
    '''
    # 存储到整体dict，帧为索引
    allData = dict()
    frame = 0
    # 读取数据
    with open(path) as f:
        for line in f.readlines():
            try:
                data = json.loads(line)
                allData[frame] = data
                frame += 1
            except:
                pass
    print("总帧数", frame+1)
    return allData

if __name__ == "__main__":
    load_data_all("../data/result.txt")