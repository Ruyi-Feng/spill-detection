from rsu_simulator import Smltor
from kafka import KafkaConsumer
from utils import loadConfig
import json
from datetime import datetime


def simulatedSave():
    dataPath = './data/result.txt'
    outputPath = './data/output.txt'
    s = Smltor(dataPath)
    with open(outputPath, 'a') as f:
        while True:
            msg = s.run()
            if msg == '':   # 读取到文件末尾
                break
            f.write(str(msg) + '\n')


def updateFilePathPerHour():
    '''每小时更新一次文件路径, 文件命名为当前时间，格式为'年-月-日-时'''
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    return f'./data/{year}-{month}-{day}-{hour}.txt'


def save():
    cfgPath = './config.yml'
    cfg = loadConfig(cfgPath)
    kc = KafkaConsumer(
        cfg['topic'], bootstrap_servers=cfg['ip'],
        api_version=tuple(cfg['producerversion']),
        group_id='save',
        )
    for msgBytes in kc:
        outputPath = updateFilePathPerHour()
        # 在文件末尾追加
        with open(outputPath, 'a') as f:
            msgStr = msgBytes.value.decode('utf-8')
            msg = json.loads(msgStr)        # dict
            f.write(json.dumps(msg) + '\n')


if __name__ == '__main__':
    # simulatedSave()
    save()
