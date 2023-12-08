# 车辆数据格式
数据传输msg:
[
    {
        "TargetId":5853,
        "XDecx":10.7,
        "YDecy":410.15,
        "ZDecz":0,
        "VDecVx":-0.27,
        "VDecVy":23.11,
        "Xsize":0.34,
        "Ysize":1.03,
        "TargetType":1,
        "Longitude":118.87636862105768,
        "Latitude":31.93871191998073,
        "Confidence":1,
        "EventType":0,
        "LineNum":5
    },
    ...
]

内部处理data:
[
    {
        msg属性,
        "a": 0,		# preprocess中计算
        "speed":0,	# preprocess中计算
        "cellorder": -1, # 该车辆所在的cell序号，preprocess中计算
    },
    ...
]

# 交通参数据格式
trafficManager属性macro:    # 根据calib得到
{
    "len":{
        laneid1: 200,   # 索引为int型
        laneid2: 200,
        ...
    }
    "q":{
        laneid1: 100,
        laneid2: 200,
        ...
    }
    "Q": 1000,
    "k":{
        laneid1: 100,
        laneid2: 200,
        ...
    }
    "v":{
        laneid1: 100,
        laneid2: 200,
        ...
    },
    "V: 100, 
}

trafficManager属性cell:     # 根据calib得到
{
    laneid1: {
        cellorder0: {
            "vCache":[100, 110, ...],
            "q": 100,
            "k": 100,
            "v": 100,
            "danger": 0.1
        },
        cellorder1: {...},
        ... 
    }, 
    laneid2: {
        cellorder0: ...,
        cellorder1: ...,
        ... 
    },
}

标定文件calib:
{
    "emgcID": [1, 8],
    "laneCoeff": [
        laneid1: [a2, a1, a0],
        laneid2: [a2, a1, a0],
        ...
    ],
    "len": [
        laneid1: 100,
        laneid2: 200,
        ...
    ],
    "sliceLine":{
        order0: [ABC / kb],  # ABC为直线方程系数, kb为斜率, 看代码情况待定
        order1: [ABC / kb],
        ...
    }
    "invalidCells":{
        laneid1: [order0, order1, ...],
        laneid2: [order0, order1, ...],
        ...
    }

}