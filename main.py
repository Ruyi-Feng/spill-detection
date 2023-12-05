import os
import json
from calibration import calibrator
from rsu_simulator import loadDataAsList
from msg_driver import receive, send
import pre_processing
import incident_detection


if __name__ == "__main__":
    # 模拟传输开启
    filePath = './data/result.txt'
    allMessages = loadDataAsList(filePath)
    
    # 模拟标定过程
    if ~os.path.exists('./calibration/config.json'):    # 没有config则标定
        clb = calibrator()
        for msg in allMessages:
            clb.recieve(msg)
        config = clb.calibration
        clb.save('./calibration/config.json')
    else:   # 有config则读取
        with open('./calibration/config.json', 'r') as f:
            config = json.load(f)

    # 模拟接受数据
    for msg in allMessages:
        # 接受数据
        msg = receive.recieve(msg)
        # 预处理
        msg = pre_processing.pre_processing(msg)
        # 事件检测
        msg = incident_detection.incident_detection(msg)
        # 发送数据
        msg = send.send(msg)
        # print(msg)
