import yaml

'''Contain commonly used functions.'''


# 默认配置适用于高速公路
defaultConfig = {"fps": 20,
                 "ifRecalib": False, "calibSeconds": 600,
                 "laneWidth": 3.75, "emgcWidth": 3.5,
                 "cellLen": 50, "q_Merge": 0,
                 "maxCompleteTime": 20, "smoothAlpha": 0.1,
                 "qDuration": 300, "calInterval": 30,
                 "eventTypes": ["spill", "stop", "lowSpeed", "highSpeed",
                                "emgcBrake", "incident", "crowd",
                                "illegalOccupation"],
                 "tTolerance": 300, "qStandard": 10000,
                 "vLateral": 0.56, "rate2": 0.1, "spillWarnFreq": 300,
                 "vStop": 2.778, "durationStop": 5,
                 "vLow": 11.11, "durationLow": 5,
                 "vHigh": 33.33, "durationHigh": 5,
                 "aEmgcBrake": 3, "durationEmgcBrake": 1,
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


def int2strID(num: int, length: int) -> str:
    '''function int2strID

    input
    -----
    num: int, 数字
    length: int, 字符串长度

    return
    ------
    str: str, 字符串

    将数字转换为指定长度的字符串, 不足的前面补零。
    '''
    return str(num).zfill(length)


def strCapitalize(str: str) -> str:
    '''function strCapitalize

    input
    -----
    str: str, 字符串

    return
    ------
    str: str, 字符串

    字符串首字母大写。
    '''
    return str[0].upper() + str[1:]
