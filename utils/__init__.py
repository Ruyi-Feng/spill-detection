import yaml
from utils.default import defaultEventTypes
from datetime import datetime


'''Contain commonly used functions.'''


# 默认配置适用于高速公路
defaultConfig = {"fps": 20,
                 "ifRecalib": False, "calibSeconds": 600,
                 "laneWidth": 3.75, "emgcWidth": 3.5,
                 "cellLen": 50, "q_Merge": 0,
                 "maxCompleteTime": 20, "smoothAlpha": 0.1,
                 "qDuration": 300, "calInterval": 30,
                 "eventTypes": defaultEventTypes,
                 "tTolerance": 300, "qStandard": 10000,
                 "vLateral": 0.56, "rate2": 0.1, "WarnFreq": 300,
                 "vStop": 2.778, "durationStop": 5,
                 "vLow": 11.11, "durationLowSpeed": 5,
                 "vHigh": 33.33, "durationHighSpeed": 5,
                 "aEmgcBrake": 3, "durationEmgcBrake": 1,
                 "dTouch": 5, "tSupervise": 20,
                 "densityCrowd": 18, "vCrowd": 16.667,
                 "durationIllegalOccupation": 5}


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
        cfg = yaml.load(f, Loader=yaml.FullLoader)
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


def checkConfigDevices(cfg: dict) -> bool:
    '''function checkConfigDevices

    input
    -----
    cfg: dict, 配置参数

    return
    ------
    bool: bool, 是否设置的设备ID和类别的数量相同
    '''
    condition = len(cfg['deviceIDs']) == len(cfg['deviceTypes'])
    hint = '设备ID与设备类型数量不匹配. 请检查config.yml'
    return condition, hint


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


def swapQuotes(input_string: str) -> str:
    '''function swapQuotes

    input
    -----
    input_string: str, 输入字符串

    return
    ------
    str: str, 输出字符串

    将字符串中的单引号和双引号互换。
    '''
    input_string = input_string.replace("'", "temp")  # 将单引号替换为临时字符串
    input_string = input_string.replace('"', "'")  # 将双引号替换为单引号
    input_string = input_string.replace("temp", '"')  # 将临时字符串替换为双引号
    return input_string


def unixMilliseconds2Datetime(unix_milliseconds: int) -> str:
    '''function unixMilliseconds2Datetime

    input
    -----
    unix_milliseconds: int, Unix毫秒时间戳

    return
    ------
    str: str, 年月日时分秒格式的字符串

    将Unix毫秒时间戳转换为年月日时分秒格式的字符串。
    '''
    # 将Unix毫秒时间戳转换为秒
    unix_seconds = unix_milliseconds / 1000.0
    # 使用datetime.fromtimestamp()将Unix时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(unix_seconds)
    # 返回年月日时分秒格式的字符串
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')


def isNotTargetDevice(msg, args):
    '''function isNotTargetDevice

    input
    -----
    msg: dict, 传来的消息
    args: argparse.Namespace, 命令行参数

    return
    ------
    bool: bool, 是否不是目标设备
    '''
    return not (msg['deviceID'] == args.deviceId)


def isInvalidMsg(msg) -> bool:
    '''function isInvalidMsg

    input
    -----
    msg: 传来的消息

    return
    ------
    bool: bool, 是否是无效消息
    '''
    return (msg is None) or (msg == '') or (not msg)


class Args:
    '''class Args

    用于模拟argparse.Namespace的类。
    '''
    def __init__(self, deviceId, deviceType):
        self.deviceId = deviceId
        self.deviceType = deviceType


def argsFromDeviceID(deviceID: str, deviceType) -> tuple:
    '''function argsFromDeviceID

    input
    -----
    deviceID: str, 设备ID
    deviceType: str/int, 设备类型
    '''
    return Args(deviceID, deviceType)
