import os
import json
import pandas as pd
from utils import swapQuotes


def loadFieldData2df(dataPath: str, deviceID: str = None,
                     deviceType: int = 1):
    '''function loadFieldData2df

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
            row = swapQuotes(row) if row[1] == '\'' else row
            row = json.loads(row)
            condition1 = row['deviceID'] == deviceID
            condition2 = row['deviceType'] == deviceType
            if (deviceID is not None) and (not (condition1 and condition2)):
                continue
            for target in row['targets']:
                target['deviceID'] = row['deviceID']
                target['deviceType'] = row['deviceType']
                deviceData.append(target)
    # 保存到DataFrame
    df = pd.DataFrame(deviceData)
    print(df)
    suffix = f'_{deviceID}_{deviceType}.csv' if deviceID is not None \
        else '.csv'
    csvPath = dataPath.replace('.txt', suffix)
    df.to_csv(csvPath, index=False)


if __name__ == '__main__':
    # dir = r'D:\myscripts\spill-detection\data\extractedData\2024-3-26-8_byDevice'
    # dir = r'D:\myscripts\spill-detection\data\extractedData\2024-4-22-10_byDevice'

    dir = r'D:\myscripts\spill-detection\data\extractedData'
    fileList = os.listdir(dir)
    for file in fileList:
        if (not file.endswith('.txt')) or ('report' in file):
            continue
        path = os.path.join(dir, file)
        loadFieldData2df(path)
        print(path, '数据完成转化为excel.')

    # path = r'D:\myscripts\spill-detection\data\extractedData\2024-3-26-9_byDevice\K68+366_1.txt'
    # loadFieldData2df(path, 'K68+366', 1)

    # filelist = [
    #     r'D:\myscripts\spill-detection\data\extractedData\K81+320_1_2024-04-23-08-10-00_2024-04-23-08-20-00.txt'
    # ]
    # for path in filelist:
    #     loadFieldData2df(path, 'K81+320', 1)
    #     print(path, '数据完成转化为excel.')
