from rsu_simulator import Smltor
from message_driver import Driver
from tests.test_data.event import events, outerEvents


# 通过
def test_driver():
    # 模拟传输开启
    # 得到allMessages
    p = './data/result.txt'
    s = Smltor(p)
    d = Driver(20)

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
        msg, events2send = d.send(cars, events)
        # 检查点2: 成功删除属性, 暂无msg输出需求, 取消该项assert
        # if len(msg) > 0:
        #     for key in interface.keys():
        #         assert interface[key] not in msg[0].keys()
        #         assert key in msg[0].keys()
        # 检查点3: 将events转为输出格式
        assert events2send == outerEvents


if __name__ == "__main__":
    test_driver()
