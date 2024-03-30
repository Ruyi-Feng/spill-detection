from utils import swapQuotes, unixMilliseconds2Datetime
from datetime import datetime
import json
import os


def extractFieldDataByTimeRange(dataPath: str, startTime: str, endTime: str):
    '''function extractFieldDataByTimeRange

    input
    -----
    dataPath: str, 数据库文件路径
    startTime: datetime, 数据提取的开始时间, 格式为'2021-01-01 00:00:00'
    endTime: datetime, 数据提取的结束时间, 格式为'2021-01-01 00:00:01'

    return
    ------
    None, 将保存提取的数据到本地

    从记录数据中提取指定时间段的数据。
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


def extracctFieldDataByDeviceID(datapath: str, deviceID: str = None,
                                deviceType: int = 1):
    '''function extracctFieldDataByDeviceID

    input
    -----
    datapath: str, 数据库文件路径
    deviceID: str, 设备ID, 若未指定, 提取所有涉及的设备数据
    deviceType: int, 设备类型

    return
    ------
    None, 将保存提取的数据到本地

    从记录数据中提取指定设备ID的数据。
    '''
    # datapath的文件名
    name = os.path.basename(datapath).split('.')[0]
    saveDir = os.path.join('./data/extractedData', name + '_byDevice')
    print('saveDir:', saveDir)
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    with open(datapath, 'r') as f:
        while True:
            data = f.readline()
            if data == '':
                break
            data = swapQuotes(data)
            data = json.loads(data)
            if len(data['targets']) == 0:
                continue
            curDeviceID, curDeviceType = data['deviceID'], data['deviceType']
            if (deviceID is not None) and (data['deviceID'] != deviceID):
                continue
            if data['deviceType'] != deviceType:
                continue
            savePath = os.path.join(
                saveDir, curDeviceID + '_' + str(curDeviceType) + '.txt')
            with open(savePath, 'a') as f2:
                f2.write(json.dumps(data) + '\n')


def extractFieldDataByDeviceTimeRange(
        dataPath: str, deviceID: str, deviceType: int,
        startTime: str = None, endTime: str = None):
    '''function extractFieldDataByDeviceTimeRange

    input
    -----
    dataPath: str, 数据库文件路径
    deviceID: str, 设备ID
    deviceType: int, 设备类型
    startTime: datetime, 数据提取的开始时间, 格式为'2021-01-01 00:00:00'
    endTime: datetime, 数据提取的结束时间, 格式为'2021-01-01 00:00:01'

    return
    ------
    None, 将保存提取的数据到本地

    从记录数据中提取指定设备ID和时间段的数据。
    '''
    # 根据设备ID和时间段命名提取文件
    extractedPath = (
        './data/extractedData/' + deviceID + '_' + str(deviceType) + '_' +
        startTime + '_' + endTime + '.txt'
        ).replace(' ', '-').replace(':', '-')
    if os.path.exists(extractedPath):
        print(f'文件{extractedPath}已存在.')
        return      # 已存在则不再提取
    startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
    endTime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
    with open(dataPath, 'r') as f:
        while True:
            data = f.readline()
            if data == '':
                break
            data = swapQuotes(data)
            data = json.loads(data)
            if len(data['targets']) == 0:
                continue
            dataTime = unixMilliseconds2Datetime(
                data['targets'][0]['timestamp'])
            dataTime = datetime.strptime(dataTime, '%Y-%m-%d %H:%M:%S')
            if (startTime is not None) and (dataTime < startTime):
                continue
            if (endTime is not None) and (dataTime > endTime):
                break
            if data['deviceID'] == deviceID and data['deviceType'] == deviceType:
                with open(extractedPath, 'a') as f2:
                    f2.write(json.dumps(data) + '\n')
    print('数据提取完成, 保存在', extractedPath)
