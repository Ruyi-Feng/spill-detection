import json
import pandas as pd


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


def loadDeviceData2df(dataPath: str, deviceID: str, deviceType: int = 1):
    '''function loadDeviceData2df

    input
    -----
    dataPath: str, 数据文件路径
    deviceID: str, 设备ID
    deviceType: int, 设备类型, 默认为1

    return
    ------
    None

    从数据文件中加载指定设备的数据, 并以DataFrame格式保存。
    '''
    # 读取数据
    deviceData = []
    with open(dataPath) as f:
        while True:
            row = f.readline()
            if row == '':
                break
            row = json.loads(row)
            condition1 = row['deviceID'] == deviceID
            condition2 = row['deviceType'] == deviceType
            if not (condition1 and condition2):
                continue
            for target in row['targets']:
                target['deviceID'] = deviceID
                target['deviceType'] = deviceType
                deviceData.append(target)
    # 保存到DataFrame
    df = pd.DataFrame(deviceData)
    print(df)
    csvPath = dataPath.replace('.txt', f'_{deviceID}_{deviceType}.csv')
    df.to_csv(csvPath, index=False)


if __name__ == "__main__":
    # loadDataAsDict("../data/result.txt")
    dirPath = "./data/extractedData/"
    fileNameList = ["2024-03-26 08-20-18_2024-03-26 08-20-42.txt",
                    "2024-03-26 08-29-51_2024-03-26 08-30-34.txt",
                    "2024-03-26 09-36-21_2024-03-26 09-41-45.txt",
                    "2024-03-26 09-41-27_2024-03-26 09-41-57.txt"]
    deviceIDList = ['K81+320',
                    'K81+866',
                    'K78+600',
                    'K73+516']
    for fileName, deviceID in zip(fileNameList, deviceIDList):
        if deviceID != 'K81+866':
            continue
        loadDeviceData2df(dirPath + fileName, deviceID)
    print("数据加载完成.")
