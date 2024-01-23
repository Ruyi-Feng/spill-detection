from rsu_simulator import Smltor


# 数据格式
# {
#     'TargetId': 5087,
#     'XDecx': 2.57,
#     'YDecy': 7,
#     'ZDecz': 0,
#     'VDecVx': 0.13,
#     'VDecVy': -19.3,
#     'Xsize': 0.47,
#     'TargetType': 1,
#     'Longitude': 118.87387669811856,
#         'Latitude': 31.935760760137626,
#     'Confidence': 1,
#     'EventType': 0,
#     'LineNum': 1
# }


def printSpecifiedData(idList: list):
    '''function printSpecifiedData

    input
    -----
    idList: list, 指定的id列表

    输出指定id的数据
    '''
    dataPath = './data/result.txt'
    smltor = Smltor(dataPath)
    # 修改键名
    interface = {
        'TargetId': 'id',
        'XDecx': 'x',
        'YDecy': 'y',
        'VDecVx': 'vx',
        'VDecVy': 'vy',
        'LineNum': 'laneID'
        }
    # 保留键值
    keys2Delete = ['ZDecz', 'TargetType', 'Xsize', 'Ysize',
                   'Longitude', 'Latitude', 'Confidence', 'EventType']
    tsCount = 0
    # 模拟接受数据
    while True:
        msg = smltor.run()
        if msg == '':   # 读取到文件末尾
            break
        if type(msg) == str:
            continue
        for target in msg:
            if target['TargetId'] not in idList:
                continue
            # 修改键名
            for key in interface.keys():
                target[interface[key]] = target[key]
                del target[key]
            # 删除键值
            for key in keys2Delete:
                del target[key]
            # 增加必要键值
            target['ax'], target['ay'], target['a'] = 0, 0, 0

            target['timeStamp'] = tsCount * 1000
            tsCount += 1
            # 手动操作生成数值
            # target['vx'], target['vy'] = 0.13, 5.0  # 低速情况
            target['vx'], target['vy'] = 0.13, 0.5  # 停车情况
            # target['ax'], target['ay'] = 0.13, 4      # 急刹车

            target['speed'] = (target['vx']**2 + target['vy']**2)**0.5
            target['speed'] = round(target['speed'])
            print([target], end=',\n')


if __name__ == "__main__":
    # 指定id数据
    idList = [5819]     # 非法占用应急车道
    idList = [9934]     # 超速

    printSpecifiedData(idList)
