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
    # 保留键值
    keys2Delete = ['ZDecz', 'Xsize', 'TargetType',
                   'Longitude', 'Latitude', 'Confidence', 'EventType']
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
            for key in keys2Delete:
                del target[key]
            # 手动操作生成数值
            # target['VDecVx'], target['VDecVy'] = 0.13, 5.0  # 低速情况
            # target['VDecVx'], target['VDecVy'] = 0.13, 1.5  # 停车情况
            print(target, ',', sep='')


if __name__ == "__main__":
    # 指定id数据
    idList = [5819]     # 非法占用应急车道
    idList = [9934]     # 超速

    printSpecifiedData(idList)
