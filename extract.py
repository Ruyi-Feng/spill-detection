import os
from data.extract_data import (
    extractFieldDataByTimeRange,
    extracctFieldDataByDeviceID,
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
    get2609K68366Data()
