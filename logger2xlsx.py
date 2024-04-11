
import os
from copy import deepcopy
from utils.default import CharTypeDict


infoDictBase = {
    'deviceID': None,
    'type': None,
    'eventID': None,
    'startTime': None,
    'endTime': None,
    'id': None,
    'start_x': None,
    'start_y': None,
    'start_lane': None,
    'start_vx': None,
    'start_vy': None,
    'start_speed': None,
    'end_x': None,
    'end_y': None,
    'end_lane': None,
    'end_vx': None,
    'end_vy': None,
    'end_speed': None
}


def _loggerPrint2Xlsx(dataPath: str):
    '''function loggerPrint2Xlsx

    input
    -----
    dataPath: str, 日志文件路径
    
    return
    ------
    pd.DataFrame, 保存日志信息到pd.DataFrame

    读取日志在控制台打印的信息, 保存到pd.DataFrame

    data信息格式
    ------------
    2024-04-01 14:06:46,697 - K78+760_1 - WARNING - __init__.py - 事件ID=20240401-A00001 - id=2车道可能有抛洒物, 元胞起点: 700, 元胞终点: 750, 危险度: 1.0004999999999453, 开始时间: 2024-03-26 08:40:37, 当前时间: 2024-03-26 08:40:37
    2024-03-31 23:42:09,958 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-B00002 - id=1605316车辆发生stop, (x,y)=[1.0, 15.0]m, lane=8, (vx,vy,speed)=[0.0, 1.0, 0.0]km/h , 开始时间2024-03-27 17:10:00.
    2024-03-31 23:42:10,924 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-H00001 - id=1605251车辆发生illegalOccupation, (x,y)=[1.0, 17.0]m, lane=8, (vx,vy,speed)=[3.0, 0.0, 0.0]km/h , 开始时间2024-03-27 17:10:00.
    2024-03-31 23:42:11,497 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-H00001 - id=1605251车辆illegalOccupation事件结束, (x,y)=[1.0, 17.0]m, lane=8, (vx,vy,speed)=[3.0, 0.0, 0.0]km/h , 开始时间2024-03-27 17:10:00, 结束时间2024-03-27 17:10:00.
    2024-03-31 23:42:39,650 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-B00002 - id=1605316车辆stop事件结束, (x,y)=[1.0, 15.0]m, lane=8, (vx,vy,speed)=[1.0, 0.0, 0.0]km/h , 开始时间2024-03-27 17:10:00, 结束时间2024-03-27 17:10:12.
    2024-03-31 23:44:47,749 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-F00005 - id=1602112,1602263车辆碰撞, (x,y)=[1.0, 16.0]m, lane=8, (vx,vy,speed)=[2.0, 1.0, 0.0]km/h (x,y)=[1.0, 16.0]m, lane=8, (vx,vy,speed)=[1.0, 4.0, 0.0]km/h
    2024-04-01 14:13:33,584 - K78+760_1 - WARNING - __init__.py - 事件ID=20240401-A31513 - id=2车道抛洒物已处理, 元胞起点: 700, 元胞终点: 750, 危险度: 1.2379999999999192, 开始时间: 2024-03-26 08:53:54, 结束时间: 2024-03-26 08:53:54

    xlsx文件格式
    ------------
    deviceID, type, eventID, id, start_x, start_y, start_lane, start_vx, start_vy, start_speed,
    end_x, end_y, end_lane, end_vx, end_vy, end_speed, startTime, endTime

    note
    -----
    报警事件信息中, 对于单车车辆, 发生事件不转入保存数据中, 结束事件转入数据中。
    发生碰撞事件, 两个车辆的相关数据, 以tuple形式保存。
    某些事件缺失某些数值时, 以None填充。
    '''
    # 读取信息文件
    with open(dataPath, 'r', encoding='utf-8') as f:
        infoList = f.readlines()
    # 保存信息到xlsx文件
    import pandas as pd
    eventDict = {}
    # 在遍历过程中, 按deviceID, eventID保存信息
    for info in infoList:
        if '事件ID' not in info:
            continue    # 其他信息
        # 读取信息
        info = info.split(' - ')
        deviceID = info[1]
        eventID = info[4].split('=')[-1]
        eventType = CharTypeDict[eventID.split('-')[1][0]]
        objectID = info[5].split('=')[1].split('车')[0]
        eventInfo = info[5]
        # 处理eventInfo
        eventInfoDict = deepcopy(infoDictBase)
        eventInfoDict = eventInfo2Dict(eventInfo)
        eventInfoDict.update({
            'deviceID': deviceID,
            'type': eventType,
            'eventID': eventID,
            'id': objectID
        })
        # 保存信息到变量
        eventDict.setdefault(deviceID, {})
        eventDict[deviceID].setdefault(eventID, deepcopy(infoDictBase))
        eventDict[deviceID][eventID].update(eventInfoDict)
    # 保存到DataFrame
    dfList = []
    for deviceID, deviceEventDict in eventDict.items():
        for eventID, eventInfo in deviceEventDict.items():
            dfList.append(eventInfo)
    df = pd.DataFrame(dfList)
    # 清除重复行
    # df.drop_duplicates(inplace=True)
    return df


def eventInfo2Dict(eventInfo: str):
    '''按开始或结束, 不同事件类别, 将eventInfo转化为字典'''
    if '抛洒物' in eventInfo:
        return spillInfo2Dict(eventInfo)
    elif '拥堵' in eventInfo:
        return crowdInfo2Dict(eventInfo)
    elif '碰撞' in eventInfo:
        return collisionInfo2Dict(eventInfo)
    else:
        return singleCarEventInfo2Dict(eventInfo)

def spillInfo2Dict(eventInfo):
    spillInfoDict = deepcopy(infoDictBase)
    if '可能' in eventInfo:
        start = eventInfo.split('元胞起点: ')[-1].split(',')[0]
        spillInfoDict['start_x'] = float(start)
        spillInfoDict['start_y'] = float(start)
        end = eventInfo.split('元胞终点: ')[-1].split(',')[0]
        spillInfoDict['end_x'] = float(end)
        spillInfoDict['end_y'] = float(end)
        spillInfoDict['start_lane'] = int(eventInfo.split('id=')[-1].split('车道')[0])
        spillInfoDict['end_lane'] = spillInfoDict['start_lane']
        spillInfoDict['startTime'] = eventInfo.split('开始时间: ')[-1].split(',')[0]
    elif '已处理' in eventInfo:
        start = eventInfo.split('元胞起点: ')[-1].split(',')[0]
        spillInfoDict['start_x'] = float(start)
        spillInfoDict['start_y'] = float(start)
        end = eventInfo.split('元胞终点: ')[-1].split(',')[0]
        spillInfoDict['end_x'] = float(end)
        spillInfoDict['end_y'] = float(end)
        spillInfoDict['start_lane'] = int(eventInfo.split('id=')[-1].split('车道')[0])
        spillInfoDict['end_lane'] = spillInfoDict['start_lane']
        spillInfoDict['startTime'] = eventInfo.split('开始时间: ')[-1].split(',')[0]
        spillInfoDict['endTime'] = eventInfo.split('结束时间: ')[-1].split(',')[0]
    else:
        raise ValueError('抛洒物事件信息错误.')
    # 删除值为None的键值对
    for key in list(spillInfoDict.keys()):
        if spillInfoDict[key] is None:
            del spillInfoDict[key]
    return spillInfoDict

def crowdInfo2Dict(eventInfo):
    # TODO 未完成
    crowdInfoDict = deepcopy(infoDictBase)
    if '解除' not in eventInfo:
        crowdInfoDict['start_lane'] = int(eventInfo.split('车道=')[-1].split(',')[0])
        crowdInfoDict['start_speed'] = float(eventInfo.split('speed=')[-1].split('km/h')[0])
        crowdInfoDict['startTime'] = eventInfo.split('开始时间')[-1].split('.')[0]
    elif '拥堵' in eventInfo:
        crowdInfoDict['end_lane'] = int(eventInfo.split('车道=')[-1].split(',')[0])
        crowdInfoDict['end_speed'] = float(eventInfo.split('speed=')[-1].split('km/h')[0])
        crowdInfoDict['startTime'] = eventInfo.split('开始时间')[-1].split('.')[0]
        crowdInfoDict['endTime'] = eventInfo.split('结束时间')[-1].split('.')[0]
    else:
        raise ValueError('拥堵事件信息错误.')
    # 删除值为None的键值对
    for key in list(crowdInfoDict.keys()):
        if crowdInfoDict[key] is None:
            del crowdInfoDict[key]
    return crowdInfoDict

def collisionInfo2Dict(eventInfo):
    '''碰撞发生即结束
        2024-03-31 23:44:47,749 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-F00005 - id=1602112,1602263车辆碰撞, (x,y)=[1.0, 16.0]m, lane=8, (vx,vy,speed)=[2.0, 1.0, 0.0]km/h (x,y)=[1.0, 16.0]m, lane=8, (vx,vy,speed)=[1.0, 4.0, 0.0]km/h
    start xy对应第一个车辆, end xy对应第二个车辆, 其他信息类似
    '''
    collisionInfoDict = deepcopy(infoDictBase)
    startXY = eventInfo.split('(x,y)=')[1].split('m')[0][1:-1].split(',')
    collisionInfoDict['start_x'] = float(startXY[0])
    collisionInfoDict['start_y'] = float(startXY[1])
    collisionInfoDict['start_lane'] = int(eventInfo.split('lane=')[-1].split(',')[0])
    startV = eventInfo.split('(vx,vy,speed)=')[1].split('km/h')[0][1:-1].split(',')
    collisionInfoDict['start_vx'] = float(startV[0])
    collisionInfoDict['start_vy'] = float(startV[1])
    collisionInfoDict['start_speed'] = float(startV[2])
    endXY = eventInfo.split('(x,y)=')[-1].split('m')[0][1:-1].split(',')
    collisionInfoDict['end_x'] = float(endXY[0])
    collisionInfoDict['end_y'] = float(endXY[1])
    collisionInfoDict['end_lane'] = int(eventInfo.split('lane=')[-1].split(',')[0])
    endV = eventInfo.split('(vx,vy,speed)=')[-1].split('km/h')[0][1:-1].split(',')
    collisionInfoDict['end_vx'] = float(endV[0])
    collisionInfoDict['end_vy'] = float(endV[1])
    collisionInfoDict['end_speed'] = float(endV[2])
    # collisionInfoDict['startTime'] = eventInfo.split('时间: ')[-1].split('.')[0]
    # collisionInfoDict['endTime'] = collisionInfoDict['startTime']
    # 删除值为None的键值对
    for key in list(collisionInfoDict.keys()):
        if collisionInfoDict[key] is None:
            del collisionInfoDict[key]
    return collisionInfoDict
       

def singleCarEventInfo2Dict(eventInfo):
    '''将单车事件信息转化为字典
    2024-03-31 23:42:09,958 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-B00002 - id=1605316车辆发生stop, (x,y)=[1.0, 15.0]m, lane=8, (vx,vy,speed)=[0.0, 1.0, 0.0]km/h , 开始时间2024-03-27 17:10:00.
    2024-03-31 23:42:10,924 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-H00001 - id=1605251车辆发生illegalOccupation, (x,y)=[1.0, 17.0]m, lane=8, (vx,vy,speed)=[3.0, 0.0, 0.0]km/h , 开始时间2024-03-27 17:10:00.
    2024-03-31 23:42:11,497 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-H00001 - id=1605251车辆illegalOccupation事件结束, (x,y)=[1.0, 17.0]m, lane=8, (vx,vy,speed)=[3.0, 0.0, 0.0]km/h , 开始时间2024-03-27 17:10:00, 结束时间2024-03-27 17:10:00.
    2024-03-31 23:42:39,650 - K81+866_1 - WARNING - __init__.py - 事件ID=20240331-B00002 - id=1605316车辆stop事件结束, (x,y)=[1.0, 15.0]m, lane=8, (vx,vy,speed)=[1.0, 0.0, 0.0]km/h , 开始时间2024-03-27 17:10:00, 结束时间2024-03-27 17:10:12.
    '''
    singleCarEventInfoDict = deepcopy(infoDictBase)
    if '发生' in eventInfo:
        startXY = eventInfo.split('(x,y)=')[-1].split('m')[0][1:-1].split(',')
        singleCarEventInfoDict['start_x'] = float(startXY[0])
        singleCarEventInfoDict['start_y'] = float(startXY[1])
        singleCarEventInfoDict['start_lane'] = int(eventInfo.split('lane=')[-1].split(',')[0])
        startV = eventInfo.split('(vx,vy,speed)=')[-1].split('km/h')[0][1:-1].split(',')
        singleCarEventInfoDict['start_vx'] = float(startV[0])
        singleCarEventInfoDict['start_vy'] = float(startV[1])
        singleCarEventInfoDict['start_speed'] = float(startV[2])
        singleCarEventInfoDict['startTime'] = eventInfo.split('开始时间')[-1].split('.')[0]
    elif '结束' in eventInfo:
        endXY = eventInfo.split('(x,y)=')[-1].split('m')[0][1:-1].split(',')
        singleCarEventInfoDict['end_x'] = float(endXY[0])
        singleCarEventInfoDict['end_y'] = float(endXY[1])
        singleCarEventInfoDict['end_lane'] = int(eventInfo.split('lane=')[-1].split(',')[0])
        endV = eventInfo.split('(vx,vy,speed)=')[-1].split('km/h')[0][1:-1].split(',')
        singleCarEventInfoDict['end_vx'] = float(endV[0])
        singleCarEventInfoDict['end_vy'] = float(endV[1])
        singleCarEventInfoDict['end_speed'] = float(endV[2])
        singleCarEventInfoDict['startTime'] = eventInfo.split('开始时间')[-1].split(',')[0]
        singleCarEventInfoDict['endTime'] = eventInfo.split('结束时间')[-1].split('.')[0]
    else:
        raise ValueError('单车事件信息错误.')
    # 删除值为None的键值对
    for key in list(singleCarEventInfoDict.keys()):
        if singleCarEventInfoDict[key] is None:
            del singleCarEventInfoDict[key]
    return singleCarEventInfoDict


def loggerPrint2Xlsx(dataPath: str):
    '''function loggerPrint2Xlsx
    
    input
    -----
    dataPath: str, 日志文件路径
    
    return
    ------
    pd.DataFrame, 保存日志信息到xlsx文件

    读取日志在控制台打印的信息, 保存到xlsx文件。
    '''
    df = _loggerPrint2Xlsx(dataPath)
    if len(df) == 0:
        return None
    # 保存到xlsx文件
    xlsxPath = dataPath.replace('.log', '.xlsx')
    df.to_excel(xlsxPath, index=False)


def _convertDeviceLogFiles2Xlsx(dirPath:str):
    '''function convertDeviceLogFiles2Xlsx

    input
    -----
    dirPath: str, 某设备日志文件夹路径

    return
    ------
    pd.DataFrame, 保存日志信息到xlsx文件

    读取某设备的日志文件夹中的所有日志文件, 保存到xlsx文件。
    '''
    fileList = os.listdir(dirPath)
    dfList = []
    for file in fileList:
        if not file.endswith('.log'):
            continue
        df = _loggerPrint2Xlsx(dirPath + '/' + file)
        if len(df) == 0:
            continue
        dfList.append(df)
    import pandas as pd
    if len(dfList) == 0:
        return pd.DataFrame()
    df = pd.concat(dfList)
    # 按设备时间排序
    # df.sort_values(by=['deviceID', 'type', 'eventID'], inplace=True)
    df.sort_values(by='startTime', inplace=True)
    return df


def convertDeviceLogFiles2Xlsx(dirPath: str):
    '''function convertDeviceLogFiles2Xlsx

    input
    -----
    dirPath: str, 某设备日志文件夹路径

    return
    ------
    None, 保存日志信息到xlsx文件

    读取某设备的日志文件夹中的所有日志文件, 保存到xlsx文件。
    '''
    df = _convertDeviceLogFiles2Xlsx(dirPath)
    if len(df) == 0:
        return
    # 保存到xlsx文件
    xlsxPath = dirPath + '.xlsx'
    df.to_excel(xlsxPath, index=False)


def _convertLoggerDirFiles2Xlsx(dirPath: str):
    '''function convertLoggerDirFiles2Xlsx

    input
    -----
    dirPath: str, 日志文件夹路径

    return
    ------
    dataFrame, 保存日志信息到dataFrame

    读取日志文件夹中的所有设备的日志文件, 保存到dataFrame
    '''
    dfList = []
    fileList = os.listdir(dirPath)
    for subfile in fileList:
        # 若为文件夹, 则调用
        if os.path.isdir(dirPath + '/' + subfile):
            df = _convertDeviceLogFiles2Xlsx(dirPath + '/' + subfile)
            if len(df) == 0:
                continue
            dfList.append(df)
    import pandas as pd
    df = pd.concat(dfList)
    # 按设备时间排序
    # df.sort_values(by=['deviceID', 'type', 'eventID'], inplace=True)
    df.sort_values(by='startTime', inplace=True)
    return df


def convertLoggerDirFiles2Xlsx(dirPath: str):
    '''function convertLoggerDirFiles2Xlsx

    input
    -----
    dirPath: str, 日志文件夹路径

    return
    ------
    None, 保存日志信息到xlsx文件

    读取日志文件夹中的所有设备的日志文件, 保存到xlsx文件。
    '''
    df = _convertLoggerDirFiles2Xlsx(dirPath)
    if len(df) == 0:
        return
    # 排序
    # df.sort_values(by=['deviceID', 'type', 'eventID'], inplace=True)
    df.sort_values(by='startTime', inplace=True)
    # 保存到xlsx文件
    xlsxPath = dirPath + '.xlsx'
    df.to_excel(xlsxPath, index=False)


def loggerInfoStatistic(xlsxPath: str):
    '''function loggerInfoStatistic
    
    input
    -----
    xlsxPath: str, 日志信息文件路径

    return
    ------
    None, 统计日志信息

    统计日志信息, 并将统计信息写入到第二个sheet中。
    '''
    import pandas as pd
    df = pd.read_excel(xlsxPath)
    # 统计信息, 按deviceId, eventType统计
    infoDict = {}
    for index, row in df.iterrows():
        deviceID = row['deviceID']
        eventType = row['type']
        info = row['eventID']
        infoDict.setdefault(deviceID, {})
        infoDict[deviceID].setdefault(eventType, [])
        infoDict[deviceID][eventType].append(info)
    # 统计次数
    for deviceID in infoDict:
        for eventType in infoDict[deviceID]:
            infoDict[deviceID][eventType] = len(infoDict[deviceID][eventType])
    # 调换infoDict的索引顺序为eventType, deviceID。使得dataframe的列为eventType
    infoDict = reverseDict2LayerKeys(infoDict)
    # 转为DataFrame
    df_statistic = pd.DataFrame(infoDict)
    # 写入xlsx文件
    with pd.ExcelWriter(xlsxPath, engine='openpyxl', mode='a') as writer:  # Use mode='a' to append data
        df_statistic.to_excel(writer, sheet_name='统计信息')  # Write the statistic data to a new sheet '统计信息'


def reverseDict2LayerKeys(d: dict):
    '''将dict的第二层键值对, 转为第一层键值对'''
    newDict = {}
    for key1 in d:
        for key2 in d[key1]:
            newDict.setdefault(key2, {})
            newDict[key2][key1] = d[key1][key2]
    return newDict

if __name__ == "__main__":
    # logger转化为xlsx
    dirList = [
        r'D:\myscripts\spill-detection\logger\logs-2608',
        r'D:\myscripts\spill-detection\logger\logs-2609',
        r'D:\myscripts\spill-detection\logger\logs-2717',
        r'D:\myscripts\spill-detection\logger\logs-2718',
    ]
    for dir in dirList:
        convertLoggerDirFiles2Xlsx(dir)
        print(dir, '日志信息保存完成.')

    # # 对logger xlsx统计
    dir = './logger'
    for file in os.listdir(dir):
        if ('logs' not in file) or (not file.endswith('.xlsx')):
            continue
        xlsxPath = dir + '/' + file
        loggerInfoStatistic(xlsxPath)
        print(xlsxPath, '日志信息统计完成.')
