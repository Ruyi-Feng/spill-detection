def preproInfo2Xlsx(infoPath: str):
    '''function preproInfo2Xlsx

    input
    -----
    infoPath: str, 预处理信息文件路径

    return
    ------
    None, 保存预处理信息到xlsx文件

    读取预处理的运行时长报告信息文件, 保存到xlsx文件。

    info信息格式
    ------------
    deviceID K81+320 count: 22800
    总耗时：151630.70ms, 平均每次耗时：6.65ms
    合并历史帧数据耗时：147539.69ms, 平均每次耗时：6.47ms, 占比：97.30%
    查找延迟帧号耗时：1616.88ms, 平均每次耗时：0.07ms, 占比：1.07%
    处理插值耗时：2474.13ms, 平均每次耗时：0.11ms, 占比：1.63%
    查找最近帧号耗时：497.27ms, 平均每次耗时：0.02ms, 占比：0.33%
    补全轨迹点耗时：0.00ms, 平均每次耗时：0.00ms, 占比：0.00%
    Interpolation report:: 2024-03-30 17:00:44.983972  dataTime:  2024-03-27 17:10:02 K81+320_1

    xlsx文件格式
    ------------
    deviceID, count, 每次ave, 合并历史帧数据ave, 查找延迟帧号ave,
    处理插值ave, 查找最近帧号ave, 补全轨迹点ave,
    合并历史帧数据ratio, 查找延迟帧号ratio, 处理插值ratio,
    查找最近帧号ratio, 补全轨迹点ratio
    '''
    # 读取信息文件
    xlsxPath = infoPath.replace('.txt', '.xlsx')
    with open(infoPath, 'r', encoding='utf-8') as f:
        infoList = f.readlines()
    # 保存信息到xlsx文件
    import pandas as pd
    infoDict = {}
    for info in infoList:
        if 'deviceID' in info:
            deviceID = info.split()[1]
            count = int(info.split()[-1])
            infoDict.setdefault(deviceID, {'count': [count]})
            infoDict[deviceID]['count'].append(count)
        if '总耗时' in info:
            totalTime = float(info.split('：')[-1].split('ms')[0])
            infoDict[deviceID].setdefault('totalTime', [totalTime])
            infoDict[deviceID]['totalTime'].append(totalTime)
        if '平均每次耗时' in info:
            aveTime = float(info.split('：')[2].split('ms')[0])
            if '合并历史帧数据' in info:
                infoDict[deviceID].setdefault('framesCombineTime', [aveTime])
                infoDict[deviceID]['framesCombineTime'].append(aveTime)
            if '查找延迟帧号' in info:
                infoDict[deviceID].setdefault('delayFramesTime', [aveTime])
                infoDict[deviceID]['delayFramesTime'].append(aveTime)
            if '处理插值' in info:
                infoDict[deviceID].setdefault('interpolationTime', [aveTime])
                infoDict[deviceID]['interpolationTime'].append(aveTime)
            if '查找最近帧号' in info:
                infoDict[deviceID].setdefault('nearFramesTime', [aveTime])
                infoDict[deviceID]['nearFramesTime'].append(aveTime)
            if '补全轨迹点' in info:
                infoDict[deviceID].setdefault('completeTracksTime', [aveTime])
                infoDict[deviceID]['completeTracksTime'].append(aveTime)
        if '占比' in info:
            ratio = float(info.split('：')[-1].split('%')[0])
            if '合并历史帧数据' in info:
                infoDict[deviceID].setdefault('framesCombineRatio', [ratio])
                infoDict[deviceID]['framesCombineRatio'].append(ratio)
            if '查找延迟帧号' in info:
                infoDict[deviceID].setdefault('delayFramesRatio', [ratio])
                infoDict[deviceID]['delayFramesRatio'].append(ratio)
            if '处理插值' in info:
                infoDict[deviceID].setdefault('interpolationRatio', [ratio])
                infoDict[deviceID]['interpolationRatio'].append(ratio)
            if '查找最近帧号' in info:
                infoDict[deviceID].setdefault('nearFramesRatio', [ratio])
                infoDict[deviceID]['nearFramesRatio'].append(ratio)
            if '补全轨迹点' in info:
                infoDict[deviceID].setdefault('completeTracksRatio', [ratio])
                infoDict[deviceID]['completeTracksRatio'].append(ratio)
    # 将dict中按设备号，将各个键所对应的list，按索引分行，保存到xlsx文件
    for deviceRunTime in infoDict:
       # 写入xlsx文件
        df = pd.DataFrame(infoDict[deviceRunTime])
        # 设定列的顺序，时间在前，占比在后
        columns = ['count', 'framesCombineTime',
                   'delayFramesTime', 'interpolationTime', 'nearFramesTime',
                   'completeTracksTime', 'totalTime', 'framesCombineRatio',
                   'delayFramesRatio', 'interpolationRatio',
                   'nearFramesRatio', 'completeTracksRatio']
        df = df[columns]
        df.to_excel(xlsxPath, sheet_name=deviceRunTime, index=None)    


def contorllerInfo2Xlsx(infoPath: str):
    '''function contorllerInfo2Xlsx

    input
    -----
    infoPath: str, 控制器信息文件路径

    return
    ------
    None, 保存控制器信息到xlsx文件

    读取控制器的运行时长报告信息文件, 保存到xlsx文件。

    info信息格式
    ------------
    time report: K81+320_1 2024-03-30 18:11:37.348286  dataTime:  2024-03-27 17:02:29 K81+320_1
    count:  6000
    驱动器平均耗时: 0.01ms, 占比: 0.50%
    交通参数计算平均耗时: 0.00ms, 占比: 0.18%
    预处理平均耗时: 2.05ms, 占比: 91.28%
    事件检测平均耗时: 0.18ms, 占比: 7.98%
    发送平均耗时: 0.00ms, 占比: 0.05%
    保存平均耗时: 0.00ms, 占比: 0.01%
    平均总耗时: 2.25ms
    总耗时: 13481.79ms

    xlsx文件格式
    ------------
    deviceID, count, 每次ave, 驱动器ave, 交通参数计算ave,
    预处理ave, 事件检测ave, 发送ave, 保存ave,
    驱动器ratio, 交通参数计算ratio, 预处理ratio,
    事件检测ratio, 发送ratio, 保存ratio

    '''
    # 读取信息文件
    xlsxPath = infoPath.replace('.txt', '.xlsx')
    with open(infoPath, 'r', encoding='utf-8') as f:
        infoList = f.readlines()
    # 保存信息到xlsx文件
    import pandas as pd
    infoDict = {}
    for info in infoList:
        if 'time report' in info:
            deviceID = info.split()[2]
        if 'count' in info:
            count = int(info.split()[-1])
            infoDict.setdefault(deviceID, {'count': [count]})
            infoDict[deviceID]['count'].append(count)
        if '平均耗时' in info:
            aveTime = float(info.split(': ')[1].split('ms')[0])
            if '驱动器' in info:
                infoDict[deviceID].setdefault('driverTime', [aveTime])
                infoDict[deviceID]['driverTime'].append(aveTime)
            if '交通参数计算' in info:
                infoDict[deviceID].setdefault('trafficTime', [aveTime])
                infoDict[deviceID]['trafficTime'].append(aveTime)
            if '预处理' in info:
                infoDict[deviceID].setdefault('preproTime', [aveTime])
                infoDict[deviceID]['preproTime'].append(aveTime)
            if '事件检测' in info:
                infoDict[deviceID].setdefault('detectTime', [aveTime])
                infoDict[deviceID]['detectTime'].append(aveTime)
            if '发送' in info:
                infoDict[deviceID].setdefault('sendTime', [aveTime])
                infoDict[deviceID]['sendTime'].append(aveTime)
            if '保存' in info:
                infoDict[deviceID].setdefault('saveTime', [aveTime])
                infoDict[deviceID]['saveTime'].append(aveTime)
        if '占比' in info:
            ratio = float(info.split(':')[-1].split('%')[0])
            if '驱动器' in info:
                infoDict[deviceID].setdefault('driverRatio', [ratio])
                infoDict[deviceID]['driverRatio'].append(ratio)
            if '交通参数计算' in info:
                infoDict[deviceID].setdefault('trafficRatio', [ratio])
                infoDict[deviceID]['trafficRatio'].append(ratio)
            if '预处理' in info:
                infoDict[deviceID].setdefault('preproRatio', [ratio])
                infoDict[deviceID]['preproRatio'].append(ratio)
            if '事件检测' in info:
                infoDict[deviceID].setdefault('detectRatio', [ratio])
                infoDict[deviceID]['detectRatio'].append(ratio)
            if '发送' in info:
                infoDict[deviceID].setdefault('sendRatio', [ratio])
                infoDict[deviceID]['sendRatio'].append(ratio)
            if '保存' in info:
                infoDict[deviceID].setdefault('saveRatio', [ratio])
                infoDict[deviceID]['saveRatio'].append(ratio)
        if '平均总耗时' in info:
            aveTotalTime = float(info.split(':')[-1].split('ms')[0])
            infoDict[deviceID].setdefault('aveTotalTime', [aveTotalTime])
            infoDict[deviceID]['aveTotalTime'].append(aveTotalTime)

    # 将dict中按设备号，将各个键所对应的list，按索引分行，保存到xlsx文件
    for deviceRunTime in infoDict:
       # 写入xlsx文件
        df = pd.DataFrame(infoDict[deviceRunTime])
        # 设定列的顺序，时间在前，占比在后
        columns = ['count', 'aveTotalTime', 'driverTime',
                   'trafficTime', 'preproTime', 'detectTime', 'sendTime',
                   'saveTime', 'driverRatio', 'trafficRatio', 'preproRatio',
                     'detectRatio', 'sendRatio', 'saveRatio']
        df.to_excel(xlsxPath, sheet_name=deviceRunTime, index=None)


if __name__ == "__main__":
    # 已ok, 请勿再次运行
    # path = r'D:\myscripts\spill-detection\data\extractedData\2024-3-27-17_byDevice\K81+320-prepro-runtime-report.txt'
    # preproInfo2Xlsx(path)
    # path = r'D:\myscripts\spill-detection\data\extractedData\2024-3-27-17_byDevice\K81+320-contorller-runtime-report.txt'
    # contorllerInfo2Xlsx(path)
    # path = r'D:\myscripts\spill-detection\data\extractedData\2024-3-27-17_byDevice\K78+760-prepro-runtime-report.txt'
    # preproInfo2Xlsx(path)
    # 即将执行
    path = r'D:\myscripts\spill-detection\data\extractedData\2024-3-27-17_byDevice\K78+760-prepro-runtime-report.txt'
    preproInfo2Xlsx(path)
    print('done.')
