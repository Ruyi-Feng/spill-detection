from utils import swapQuotes, unixMilliseconds2Datetime
from datetime import datetime
import json
import os


def extractEventDataFromDataBase(dataPath: str, startTime: str, endTime: str):
    '''function extractEventDataFromDataBase

    从数据库中提取数据, 用于离线测试。

    input
    -----
    dataPath: str, 数据库文件路径
    startTime: datetime, 数据提取的开始时间, 格式为'2021-01-01 00-00-00'
    endTime: datetime, 数据提取的结束时间, 格式为'2021-01-01 00-00-00'

    return
    ------
    None, 将保存提取的数据到本地
    '''
    # 根据起止时间命名提取文件
    extractedPath = ('./data/extractedData/' + startTime + \
        '_' + endTime + '.txt').replace(' ', '-').replace(':', '-')
    if os.path.exists(extractedPath):
        print(f'文件{extractedPath}已存在.')
        return      # 已存在则不再提取
    startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
    endTime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
    # 根据起止时间命名提取文件
    with open(dataPath, 'r') as f:
        while True:
            data = f.readline()
            data = swapQuotes(data)
            data = json.loads(data)
            if len(data['targets']) == 0:
                continue
            dataTime = unixMilliseconds2Datetime(
                data['targets'][0]['timestamp'])
            dataTime = datetime.strptime(dataTime, '%Y-%m-%d %H:%M:%S')
            if dataTime < startTime:
                continue
            if dataTime > endTime:
                break
            with open(extractedPath, 'a') as f2:
                f2.write(json.dumps(data) + '\n')
    print('数据提取完成, 保存在', extractedPath)


if __name__ == "__main__":
    dataPath2TimeRangeDict = {
        'D:/东南大学/科研/金科/data/2024-3-26-0.txt': [
            ['2024-03-26 08:20:18', '2024-03-26 08:20:42'],
            ['2024-03-26 08:29:51', '2024-03-26 08:30:34']
            ],
        'D:/东南大学/科研/金科/2024-3-26-1.txt': [
            ['2024-03-26 09:36:21', '2024-03-26 09:41:45'],
            ['2024-03-26 09:41:27', '2024-03-26 09:41:57']
            ],
        'D:/东南大学/科研/金科/data/dataRy/data/2024-3-27-18.txt': [
            ['2024-03-27 18:38:15', '2024-03-27 18:42:15'],
            ['2024-03-27 18:42:33', '2024-03-27 18:46:33'],
            ['2024-03-27 18:50:08', '2024-03-27 18:54:08']
            ],
        'D:/东南大学/科研/金科/data/dataRy/data/2024-3-27-17.txt': [
            ['2024-03-27 16:53:16', '2024-03-27 16:57:16']
            ]
    }
    for path, timeRangeList in dataPath2TimeRangeDict.items():
        for timeRange in timeRangeList:
            extractEventDataFromDataBase(path, timeRange[0], timeRange[1])
    print('数据提取完成.')
