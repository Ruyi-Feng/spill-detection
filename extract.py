import os
from data.extract_data import (
    extractFieldDataByTimeRange,
    extracctFieldDataByDeviceID,
    extractFieldDataByDeviceTimeRange,
    extractEventDataByPlatformWarn,
)
from data.observe_data import (
    observeFieldData,
    getAverageTimeStepForSingleDevice
)

def extractSpecifiedTimeRangeToDetectEvent():
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
            extractFieldDataByTimeRange(path, timeRange[0], timeRange[1])
    print('数据提取完成.')


def extract20240327EveningPeakDataByDevice():
    dataPath = 'D:/东南大学/科研/金科/data/dataRy/data/2024-3-27-17.txt'
    extracctFieldDataByDeviceID(dataPath)


def observe20240327EveningPeakData():
    dataPath = 'D:/东南大学/科研/金科/data/dataRy/data/2024-3-27-17.txt'
    observeFieldData(dataPath, ifSave=True)


def observeTimeStep20240327EveningPeak():
    dataDir = r'D:\myscripts\spill-detection\data\extractedData\2024-3-27-17_byDevice'
    for file in os.listdir(dataDir):
        if not file.endswith('.txt'):
            continue
        getAverageTimeStepForSingleDevice(dataDir + '/' + file)


def get260820data():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-26-8.txt'
    extractFieldDataByTimeRange(dataPath, '2024-03-26 08:15:00', '2024-03-26 08:25:00')
    print('数据提取完成.')


def get2608DeviceData():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-26-8.txt'
    extracctFieldDataByDeviceID(dataPath)


def get2609DeviceData():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-26-9.txt'
    extracctFieldDataByDeviceID(dataPath)

def get2717DeviceData():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-27-17.txt'
    extracctFieldDataByDeviceID(dataPath)

def get2718DeviceData():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-27-18.txt'
    extracctFieldDataByDeviceID(dataPath)

def get2609K68366Data():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-26-9.txt'
    deviceID = 'K68+366'
    extracctFieldDataByDeviceID(dataPath, deviceID)


def get2717SecondHalfData():
    dataPath = r'D:\东南大学\科研\金科\data\dataRy\data/2024-3-27-17.txt'
    extractFieldDataByTimeRange(dataPath, '2024-03-27 17:30:00', '2024-03-27 17:40:00')
    print('数据提取完成.')


def observe042210data():
    dataPath = r'E:\data\2024-4-22-10.txt'
    observeFieldData(dataPath, ifSave=True)


def get042210data():
    dataPath = r'E:\data\2024-4-22-10.txt'
    extracctFieldDataByDeviceID(dataPath)
    print('数据提取完成.')


# def extractEventDataByPlatformWarn042223():
#     warnPath = r'D:\myscripts\spill-detection\analysis\4月22，23日全天数据\事件明细[2024-04-22-2024-04-23]4月下旬测试.xlsx'
#     dataDir = r'E:\data'
#     extractEventDataByPlatformWarn(warnPath, dataDir)


def get04dataK68366():
    datadir = r'E:\data'
    deviceID = 'K68+366'
    for file in os.listdir(datadir):
        if not file.endswith('.txt'):
            continue
        dataPath = os.path.join(datadir, file)
        extracctFieldDataByDeviceID(dataPath, deviceID)
        print(dataPath, '数据提取完成.')


def observe04data():
    datadir = r'E:\data'
    for file in os.listdir(datadir):
        if not file.endswith('.txt'):
            continue
        dataPath = os.path.join(datadir, file)
        observeFieldData(dataPath, ifSave=True)
        print(dataPath, '数据观察完成.')


def get0424K68366dataFrom14To18():
    dir = r'E:\data'
    filename = [
        '2024-4-23-14.txt',
        '2024-4-23-15.txt',
        '2024-4-23-16.txt',
        '2024-4-23-18.txt',
    ]
    deviceID = 'K68+366'
    for file in filename:
        dataPath = os.path.join(dir, file)
        extracctFieldDataByDeviceID(dataPath, deviceID)
        print(dataPath, '数据提取完成.')


def get042223dataK79886forillegalOccupation():
    dir = r'E:\data'
    filename = [
        '2024-4-22-13.txt',
        '2024-4-22-14.txt',
        '2024-4-22-15.txt',
        '2024-4-22-16.txt',
        '2024-4-22-17.txt',
        '2024-4-23-8.txt',
        '2024-4-23-9.txt',
    ]
    deviceID = 'K79+886'
    for file in filename:
        dataPath = os.path.join(dir, file)
        extracctFieldDataByDeviceID(dataPath, deviceID)
        print(dataPath, '数据提取完成.')


def get202404230810to20dataK81320():
    dir = r'E:\data'
    filename = '2024-4-23-8.txt'
    deviceID = 'K81+320'
    startTime = '2024-04-23 08:10:00'
    endTime = '2024-04-23 08:20:00'
    extractFieldDataByDeviceTimeRange(dir + '/' + filename, deviceID, 1, startTime, endTime)


if __name__ == "__main__":
    # extractSpecifiedTimeRangeToDetectEvent()
    # extract20240327EveningPeakDataByDevice()  # 已提取, 勿重复
    # observe20240327EveningPeakData()
    # observeTimeStep20240327EveningPeak()
    # get260820data()
    # get2608DeviceData()
    # get2609DeviceData()
    # get2717DeviceData()
    # get2718DeviceData()
    # get2609K68366Data()
    # get2717SecondHalfData()
    # observe042210data()
    # get042210data()
    # extractEventDataByPlatformWarn042223()
    # get04dataK68366()
    # observe04data()
    # get0424K68366dataFrom14To18()
    # get042223dataK79886forillegalOccupation()
    # get202404230810to20dataK81320()
