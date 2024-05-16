import os
import json
from utils import swapQuotes, unixMilliseconds2Datetime
from utils.file_read import BigFileReader


def observeFieldData(dataPath: str, ifSave: bool = False):
    '''function observeFieldData

    input
    -----
    dataPath: str, 数据库文件路径
    ifSave: bool, 是否保存信息数据表格到本地
    数据表格信息:
    设备名称, 设备类型, 开始时间戳(可读格式), 结束时间戳(可读格式), 数据条数,
    并对各设备每条数据targets的数量进行统计, 包含最大, 最小, 平均值, 中位数。

    return
    ------
    None, 打印数据文件信息

    读取数据文件, 打印数据文件信息。
    '''
    reader = BigFileReader(dataPath)
    rowNum = reader.rowNumber
    print(f'{dataPath} has {rowNum} rows.')
    # 生成可转为dataFrame的存储dict变量
    baseInfo = ['startTimeStamp', 'endTimeStamp', 'messageNum',
                'targetsNumList',
                'maxTargetsNum', 'minTargetsNum', 'meanTargetsNum',
                'medianTargetsNum']
    infoDict = dict()   # 一层索引deviceID, 二层索引deviceType, 三层索引baseInfo
    for i in range(rowNum):
        data = reader.getRow(i)
        if data[2] == '\'':
            data = swapQuotes(data)
        data = json.loads(data)
        deviceID = data['deviceID']
        deviceType = data['deviceType']
        if deviceID not in infoDict:
            infoDict[deviceID] = dict()
        if deviceType not in infoDict[deviceID]:
            infoDict[deviceID][deviceType] = dict()
            for info in baseInfo:
                infoDict[deviceID][deviceType][info] = 0
            infoDict[deviceID][deviceType]['targetsNumList'] = []
        # 更新信息
        if len(data['targets']) == 0:
            continue
        # 时间戳
        timestamp = data['targets'][0]['timestamp']
        if infoDict[deviceID][deviceType]['startTimeStamp'] == 0:
            infoDict[deviceID][deviceType]['startTimeStamp'] = timestamp
            infoDict[deviceID][deviceType]['endTimeStamp'] = timestamp
        else:
            if timestamp < infoDict[deviceID][deviceType]['startTimeStamp']:
                infoDict[deviceID][deviceType]['startTimeStamp'] = timestamp
            if timestamp > infoDict[deviceID][deviceType]['endTimeStamp']:
                infoDict[deviceID][deviceType]['endTimeStamp'] = timestamp
        # 数据条数
        infoDict[deviceID][deviceType]['messageNum'] += 1
        # targets数量
        targetsNum = len(data['targets'])
        infoDict[deviceID][deviceType]['targetsNumList'].append(targetsNum)
    # 记录结束, 计算targets数量信息
    for deviceID in infoDict:
        for deviceType in infoDict[deviceID]:
            targetsNumList = infoDict[deviceID][deviceType]['targetsNumList']
            infoDict[deviceID][deviceType]['maxTargetsNum'] = max(targetsNumList)
            infoDict[deviceID][deviceType]['minTargetsNum'] = min(targetsNumList)
            infoDict[deviceID][deviceType]['meanTargetsNum'] = sum(
                targetsNumList) / len(targetsNumList)
            targetsNumList.sort()
            infoDict[deviceID][deviceType]['medianTargetsNum'] = targetsNumList[
                len(targetsNumList) // 2]
    # 打印信息
    for deviceID in infoDict:
        for deviceType in infoDict[deviceID]:
            print(f'{deviceID}_{deviceType}:')
            for info in baseInfo:
                if info == 'targetsNumList':
                    continue
                if info in ['startTimeStamp', 'endTimeStamp']:
                    print(f'    {info}: {unixMilliseconds2Datetime(infoDict[deviceID][deviceType][info])}')
                else:
                    print(f'    {info}: {infoDict[deviceID][deviceType][info]}')
    # 保存信息
    if ifSave:
        import pandas as pd
        dir = os.path.dirname(dataPath)
        fileName = os.path.basename(dataPath)
        savePath = os.path.join(dir, fileName.split('.')[0] + '_info.csv')
        infoList = []
        for deviceID in infoDict:
            for deviceType in infoDict[deviceID]:
                info = infoDict[deviceID][deviceType]
                infoList.append([deviceID, deviceType,
                                 unixMilliseconds2Datetime(info['startTimeStamp']),
                                 unixMilliseconds2Datetime(info['endTimeStamp']),
                                 info['messageNum'],
                                 info['maxTargetsNum'], info['minTargetsNum'],
                                 info['meanTargetsNum'], info['medianTargetsNum']])
        df = pd.DataFrame(infoList, columns=['deviceID', 'deviceType',
                                             'startTime', 'endTime', 'messageNum',
                                             'maxTargetsNum', 'minTargetsNum',
                                             'meanTargetsNum', 'medianTargetsNum'])
        df.to_csv(savePath, index=False)
        print(f'数据信息保存在{savePath}')


def getAverageTimeStepForSingleDevice(dataPath: str):
    '''function getAverageTimeStepForSingleDevice

    input
    -----
    dataPath: str, 数据库文件路径

    return
    ------
    None, 打印数据文件信息

    读取数据文件, 打印数据文件信息。
    '''
    reader = BigFileReader(dataPath)
    rowNum = reader.rowNumber
    print(f'{dataPath} has {rowNum} rows.')
    timeList = []
    for i in range(rowNum):
        data = reader.getRow(i)
        # data = swapQuotes(data)
        data = json.loads(data)
        deviceID = data['deviceID']
        deviceType = data['deviceType']
        if len(data['targets']) == 0:
            continue
        timeList.append(data['targets'][0]['timestamp'])
    timeList.sort()
    timeStepList = []
    for i in range(1, len(timeList)):
        timeStepList.append(timeList[i] - timeList[i - 1])
    print(deviceID, deviceType,
        'average time step:', sum(timeStepList) / len(timeStepList))
