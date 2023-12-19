from rsu_simulator import Smltor
from msg_driver import Driver
from pathlib import Path


# 通过
def test_driver():
    # 模拟传输开启
    # 得到allMessages
    p = (Path(__file__) / './../../data/result.txt').resolve()
    s = Smltor(str(p))
    d = Driver()

    while True:
        msg = s.run()
        if msg == '':
            break
        if type(msg) == str:    # 非目标信息
            continue

        # 模拟接受数据
        # print('接收前', msg[0])
        # 接受数据
        msg = d.receive(msg)
        # print('代码内', msg[0])
        # 发送数据
        msg = d.send(msg)
        # print('发送', msg[0])
        # 断点
        # print('------------------')

    assert type(msg) == str


if __name__ == "__main__":
    test_driver()
