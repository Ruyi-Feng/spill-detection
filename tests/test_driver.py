from rsu_simulator.dataloader import loadDataAsList
from msg_driver import Driver
import json


# 通过
def test_driver():
    # 模拟传输开启
    # 得到allMessages
    filePath = './data/result.txt'
    allMessages = loadDataAsList(filePath)

    d = Driver()
    # 模拟接受数据
    for msg in allMessages:
        print('接收前', msg[0])
        # 接受数据
        msg = d.receive(msg)
        print('代码内', msg[0])
        # 发送数据
        msg = d.send(msg)
        print('发送', msg[0])
        # 断点
        print('------------------')


if __name__ == "__main__":
    json.load('kasdjf')
    test_driver()
