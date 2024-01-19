import yaml

'''Contain commonly used functions.'''


# 默认配置适用于高速公路
defaultEventTypes = ['spill', 'stop', 'lowSpeed', 'highSpeed',
                     'emergencyBrake', 'incident', 'crowd',
                     'illegalOccupation']
defaultConfig = {"fps": 20,
                 "ifRecalib": False, "calibSeconds": 600,
                 "laneWidth": 3.75, "emgcWidth": 3.5,
                 "cellLen": 50, "q_Merge": 0,
                 "maxCompleteFrames": 20, "smoothAlpha": 0.1,
                 "qDuration": 300, "calInterval": 30,
                 "eventTypes": ["spill", "stop", "lowSpeed", "highSpeed",
                                "emergencyBrake", "incident", "crowd",
                                "illegalOccupation"],
                 "tTolerance": 300, "qStandard": 10000,
                 "vLateral": 0.56, "rate2": 0.1, "spillWarnFreq": 300,
                 "vStatic": 2.778, "durationStatic": 5,
                 "vLow": 11.11, "durationLow": 5,
                 "vHigh": 33.33, "durationHigh": 5,
                 "aIntense": 3, "durationIntense": 1,
                 "dTouch": 5, "tSupervise": 20,
                 "densityCrowd": 18, "vCrowd": 16.667,
                 "durationOccupation": 5}


def loadConfig(path: str) -> dict:
    '''function _loadConfig

    input
    -----
    path: str, 文件路径

    return
    ------
    cfg: dict, 配置参数

    读取confgig.yml文件, 返回dict, 并为没有设置的参数置为默认值。
    '''
    with open(path, 'r') as f:
        cfg = yaml.load(f)
    # 为缺失的配置设置默认值
    for param in defaultConfig:
        cfg.setdefault(param, defaultConfig[param])
    return cfg


def loadYaml(path: str) -> dict:
    '''function loadYaml

    input
    -----
    path: str, 文件路径

    return
    ------
    dic: dict, yml文件内容
    '''
    with open(path, 'r') as f:
        dic = yaml.load(f, Loader=yaml.FullLoader)
    return dic


def updateDictCount(dic: dict, key: any):
    '''function updateDictCount

    input
    ------
    dic: dict, 潜在事件记录字典
    key: any, 键, 如id, id组合的列表/元胞等

    更新字典, 为id对应的车辆计数加一。
    '''
    dic.setdefault(key, 0)
    dic[key] += 1


def delDictKeys(dic: dict, keys: list):
    '''function delDictKeys

    input
    ------
    dic: dict, 潜在事件记录字典
    keys: list, 键列表

    删除字典中的指定键。
    '''
    for key in keys:
        if key in dic:
            del dic[key]
