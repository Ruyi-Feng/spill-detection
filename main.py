import os
import json
from calibration import Calibrator
from rsu_simulator.dataloader import loadDataAsList
from msg_driver import receive, send
import pre_processing
from event_detection import event_detection


if __name__ == "__main__":
    # 读取算法参数
    # 得到param
    with open('./param.json', 'r') as f:
        param = json.load(f)

    # 模拟传输开启
    # 得到allMessages
    filePath = './data/result.txt'
    allMessages = loadDataAsList(filePath)
    
    # 模拟标定过程
    # 得到config
    if ~os.path.exists('./calibration/config.json'):    # 没有config则标定
        clb = Calibrator()
        for msg in allMessages:
            clb.recieve(msg)
        config = clb.calibration
        clb.save('./calibration/config.json')
    else:   # 有config则读取
        with open('./calibration/config.json', 'r') as f:
            config = json.load(f)

    # 模拟接受数据
    traffic = []
    for msg in allMessages:
        # 接受数据
        msg = receive.recieve(msg)
        # 预处理
        msg, traffic = pre_processing.pre_processing(msg, traffic)
        # 事件检测
        msg = event_detection(msg)
        # 发送数据
        msg = send.send(msg)
        # print(msg)
