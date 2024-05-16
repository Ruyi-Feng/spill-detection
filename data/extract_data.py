from utils import swapQuotes, unixMilliseconds2Datetime
from datetime import datetime
import json
import os
import pandas as pd


extractedDir = 'D:/myscripts/spill-detection/data/extractedData'



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
    startTime = startTime.replace(':', '-')
    endTime = endTime.replace(':', '-')
    # 根据起止时间命名提取文件
    extractedPath = ('./data/extractedData/' + startTime + \
        '_' + endTime + '.txt').replace(' ', '-')
    if os.path.exists(extractedPath):
        print(f'文件{extractedPath}已存在.')
        return      # 已存在则不再提取
    startTime = datetime.strptime(startTime, '%Y-%m-%d %H-%M-%S')
    endTime = datetime.strptime(endTime, '%Y-%m-%d %H-%M-%S')
    # 根据起止时间命名提取文件
    with open(dataPath, 'r') as f:
        while True:
            data = f.readline()
            if data[2] == '\'':
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
            if data[2] == '\'':
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
    startTime = startTime.replace(':', '-')
    endTime = endTime.replace(':', '-')
    # 根据设备ID和时间段命名提取文件
    extractedPath = (
        extractedDir + '/' + deviceID + '_' + str(deviceType) + '_' +
        startTime + '_' + endTime + '.txt'
        ).replace(' ', '-')
    if os.path.exists(extractedPath):
        print(f'文件{extractedPath}已存在.')
        return      # 已存在则不再提取
    startTime = datetime.strptime(startTime, '%Y-%m-%d %H-%M-%S')
    endTime = datetime.strptime(endTime, '%Y-%m-%d %H-%M-%S')
    with open(dataPath, 'r') as f:
        while True:
            data = f.readline()
            if data == '':
                break
            if data[2] == '\'':
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


def extractEventDataByPlatformWarn(platformWarnFile: str, fieldDataDir: str):
    '''function extractEventDataByPlatformWarn

    input
    -----
    platformWarnFile: str, 平台报警文件路径
    fieldDataDir: str, 现场数据文件夹路径，可能包含多个小时数据

    return
    ------
    None, 将保存提取的数据到本地

    从平台报警文件中提取事件数据, 根据device和startTime提取。
    
    函数过程
    -------
    遍历fileDataDir下所有的数据文件
    根据warn的strattime信息, 确认要提取的数据日期和小时
    如果不在当前遍历的数据文件中, 则跳过
    否则, 提取startTime前后1min的数据并保存
    '''
    # 读取平台报警文件
    warnDf = pd.read_excel(platformWarnFile)
    condition1 = warnDf['来源'] == '雷达事件'
    condition2 = warnDf['事件类型'] == '违法停车'
    condition = [m & n for m, n in zip(condition1, condition2)]
    warnDf = warnDf[condition]
    # 遍历现场数据文件夹
    fileList = os.listdir(fieldDataDir)
    # 遍历warnDf
    for i in range(warnDf.shape[0]):
        # 获取当前warn信息
        deviceID = warnDf['相机名称'].iloc[i][:7]
        time = warnDf['发生时间'].iloc[i]
        if type(time) != str:
            time = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')
        hour = time.split(':')[0].replace(' ', '-')
        hour = '-'. join([x[1:] if x[0] == '0' else x
                            for x in hour.split('-')])
        for file in fileList:
            if (not file.endswith('.txt')) or ('report' in file):
                continue
            # 判断当前warn是否在当前file中
            if hour not in file:
                continue
            # 提取startTime前后1min的数据
            dataPath = os.path.join(fieldDataDir, file)
            startTime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            startTime = startTime - pd.Timedelta(minutes=1)
            startTime = datetime.strftime(startTime, '%Y-%m-%d %H:%M:%S')
            endTime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            endTime = endTime + pd.Timedelta(minutes=1)
            endTime = datetime.strftime(endTime, '%Y-%m-%d %H:%M:%S')
            extractFieldDataByDeviceTimeRange(
                dataPath, deviceID, 1, startTime, endTime)
