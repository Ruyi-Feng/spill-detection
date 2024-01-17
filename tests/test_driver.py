from rsu_simulator import Smltor
from message_driver import Driver


# 通过
def test_driver():
    # 模拟传输开启
    # 得到allMessages
    p = './data/result.txt'
    s = Smltor(p)
    d = Driver()

    # 测试数据转化接口
    interface = {'TargetId': 'id',
                 'XDecx': 'x',
                 'YDecy': 'y',
                 'VDecVx': 'vx',
                 'VDecVy': 'vy',
                 'Xsize': 'width',
                 'Ysize': 'length',
                 'TargetType': 'class',
                 'LineNum': 'laneID'
                 }

    while True:
        msg = s.run()
        if msg == '':
            break

        # 模拟接受数据
        valid, cars = d.receive(msg)
        if not valid:
            continue

        # 检查点1: 成功增加属性
        if len(cars) > 0:
            for key in interface.keys():
                assert interface[key] in cars[0].keys()
                assert key not in cars[0].keys()

        # 发送数据
        msg = d.send(cars)
        # 检查点2: 成功删除属性
        if len(cars) > 0:
            for key in interface.keys():
                assert interface[key] not in cars[0].keys()
                assert key in cars[0].keys()
