from rsu_simulator import Smltor
from message_driver import Driver


# 通过
def test_driver():
    # 模拟传输开启
    # 得到allMessages
    p = './data/result.txt'
    s = Smltor(p)
    d = Driver()

    while True:
        msg = s.run()
        if msg == '':
            break
        if type(msg) == str:    # 非目标信息
            continue

        # 模拟接受数据
        # print('接收前', msg[0])
        valid, cars = d.receive(msg)
        if not valid:
            continue
        # print('代码内', msg[0])
        # 检查点1
        # 成功增加属性
        if len(cars) > 0:
            assert cars[0]['a'] == 0

        # 发送数据
        msg = d.send(cars)
        # 检查点2
        # 成功删除属性
        if len(cars) > 0:
            assert 'a' not in cars[0].keys()
        # print('发送', msg[0])
        # print('------------------')

    # 检查点3
    # 数据最后一行为str 
    assert type(msg) == str
