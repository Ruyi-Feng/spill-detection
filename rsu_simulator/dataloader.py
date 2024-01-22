import json


def loadDataByLine(path: str) -> None:
    '''function loadDataByLine

    input
    ------
    path: str
        txt文件路径。txt文件按行存有msg, msg为list格式, list元素为代表车辆目标的dict。

    return
    ------
    None

    按行加载读取轨迹txt数据, 可打印输出。
    '''
    with open(path) as f:
        for line in f.readlines():
            # print(line)
            try:
                data = json.loads(line)
                print(data[0])
            except Exception:
                pass


def loadDataAsDict(path: str) -> dict:
    '''function loadDataAsDict

    input
    ------
    path: str
        txt文件路径。txt文件按行存有msg, msg为list格式, list元素为代表车辆目标的dict。

    return
    ------
    allData: dict
        以帧为索引的dict, 每帧的数据为list, list元素为代表车辆目标的dict。

    从txt文件中加载msg, 以{frame:[]target}的组织格式返回。
    '''
    # 存储到整体dict, 帧为索引
    allData = dict()
    frame = 0
    # 读取数据
    with open(path) as f:
        for line in f.readlines():
            try:
                data = json.loads(line)
                allData[frame] = data
                frame += 1
            except Exception:
                # print(type(line), line, end='')
                pass
    print("总帧数", frame+1)
    return allData


def loadDataAsList(path: str) -> list:
    '''function loadDataAsList

    input
    ------
    path: str
        txt文件路径。txt文件按行存有msg, msg为list格式, list元素为代表车辆目标的dict。

    return
    ------
    allData: list
        每帧的数据为list, list元素为代表车辆目标的dict。

    从txt文件中加载msg, 以[[]target, []target, []target, ...]的组织格式返回。
    '''
    # 存储到整体dict, 帧为索引
    allData = []
    frame = 0
    # 读取数据
    with open(path) as f:
        for line in f.readlines():
            try:
                data = json.loads(line)
                allData.append(data)
                frame += 1
            except Exception:
                # print(type(line), line, end='')
                pass
    # print("总帧数", frame+1)
    return allData


if __name__ == "__main__":
    loadDataAsDict("../data/result.txt")
