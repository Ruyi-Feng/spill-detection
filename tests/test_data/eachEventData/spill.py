elementData = [
    {'id': 9934, 'x': 2.36, 'y': 25, 'vx': 0.13, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9935, 'x': 2.36, 'y': 75, 'vx': 0.13, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9936, 'x': 2.36, 'y': 125, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    # 150-200米出现spill, 没有该段车辆
    # 并导致按行驶顺序的此段之前的200-250米的车辆横向速度变化
    {'id': 9937, 'x': 2.36, 'y': 225, 'vx': 1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9938, 'x': 2.36, 'y': 275, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9939, 'x': 2.36, 'y': 325, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9940, 'x': 2.36, 'y': 375, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9941, 'x': 2.36, 'y': 425, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9942, 'x': 2.36, 'y': 475, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9943, 'x': 2.36, 'y': 525, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9944, 'x': 2.36, 'y': 575, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9945, 'x': 2.36, 'y': 625, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9946, 'x': 2.36, 'y': 675, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9947, 'x': 2.36, 'y': 725, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20},
    {'id': 9948, 'x': 2.36, 'y': 775, 'vx': 0.1, 'vy': 20,
     'laneID': 4, 'ax': 0, 'ay': 0, 'a': 0, 'timeStamp': 0, 'speed': 20}
]

dataSpill = [elementData] * 20

dataSpillEvent = {
    'name': 'spill',
    'occured': True,
    'items':
    {
        'A0000000':
        {
            'type': 'spill',
            'eventID': 'A0000000',
            'time': 0,
            'laneID': 4,
            'order': 12,
            'start': 150.0,
            'end': 200.0,
            'danger': 1.0999999999999999
        }
    }
}
