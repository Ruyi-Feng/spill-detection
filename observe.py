import os
import json
from utils import swapQuotes, unixMilliseconds2Datetime
from utils.file_read import BigFileReader


if __name__ == '__main__':
    dataDir = r'D:\东南大学\科研\金科\data'
    for file in os.listdir(dataDir):
        if ('dump' in file) or ('result' in file) or ('heartbeat' in file):
            continue
        if 'index' in file:
            continue
        path = dataDir + '/' + file
        reader = BigFileReader(path)
        rowNum = reader.rowNumber
        print(f'{file} has {rowNum} rows.')
        row0 = reader.getRow(0)
        row0 = json.loads(swapQuotes(row0))
        rowEnd = reader.getRow(rowNum - 2)
        rowEnd = json.loads(swapQuotes(rowEnd))
        timeStart = unixMilliseconds2Datetime(row0['targets'][0]['timestamp'])
        timeEnd = unixMilliseconds2Datetime(rowEnd['targets'][0]['timestamp'])
        print(f'{file} starts at {timeStart}, ends at {timeEnd}.')
