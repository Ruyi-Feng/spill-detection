# -*-coding=utf-8-*-
import json

def loadDataByLine(path):
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


def loadDataAsDict(path):
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

def loadDataAsList(path):
    '''
    加载txt数据，并保存到一个list中.
    txt数据格式：
    每行为一帧的目标，形式为list，其中元素为代表目标信息的dict。
    返回的组织格式[[]target, []target, []target, ...]。
    '''
    # 存储到整体dict，帧为索引
    allData = []
    frame = 0
    # 读取数据
    with open(path) as f:
        for line in f.readlines():
            try:
                data = json.loads(line)
                allData.append(data)
                frame += 1
            except:
                pass
    print("总帧数", frame+1)
    return allData

if __name__ == "__main__":
    loadDataAsDict("../data/result.txt")