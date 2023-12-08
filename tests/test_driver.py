from rsu_simulator.dataloader import loadDataAsList
from msg_driver import receive, send

# 通过
def driver_test():
    # 模拟传输开启
    # 得到allMessages
    filePath = './data/result.txt'
    allMessages = loadDataAsList(filePath)
    
    # 模拟接受数据
    for msg in allMessages:
        print('接收前', msg[0])
        # 接受数据
        msg = receive(msg)
        print('代码内', msg[0])
        # 发送数据
        msg = send(msg)
        print('发送', msg[0])
        # 断点
        print('------------------')

if __name__ == "__main__":
    driver_test()