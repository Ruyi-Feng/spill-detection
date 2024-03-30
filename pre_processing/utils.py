"""Define functions to process frame data."""
import time

MaxSecMark = 60000
# 以下参数根据算法所需数据量确定, 算法最多需要2s的历史数据, 大于2.5s的数据即可删除
HistoricalInterval = 1600  # 同一id最多缓存的历史数据时长, 过老数据将被删除
UpdateInterval = 1600  # 某一id可容忍的不更新数据的时间范围


def frameDelete(contextFrames: dict, lastTimestamp: int) -> None:
    """function frameDelete

    input
    -----
    contextFrames: dict, 历史帧数据
    lastTimestamp: int, 上一帧的时间戳

    删除同一guid过老旧数据, 以及删除过久没有更新过的guid所有数据。进行原地修改。
    """
    guid_list = list(contextFrames.keys())
    for guid in guid_list:
        # 删除过老旧数据
        if (
            lastTimestamp - contextFrames[guid][0]["timestamp"]
            > HistoricalInterval
        ):
            del contextFrames[guid][0]
        # 删除过久没有更新过的guid所有数据
        if (
            len(contextFrames[guid]) == 0
            or lastTimestamp - contextFrames[guid][-1]["timestamp"]
            > UpdateInterval
        ):
            del contextFrames[guid]


def framesCombination(
    contextFrames: dict, currentFrame: dict, lastTimestamp: int
) -> tuple:
    """function framesCombination

    input
    -----
    contextFrames: dict, 历史帧数据
    currentFrame: dict, 当前帧数据
    lastTimestamp: int, 上一帧的时间戳

    output
    ------
    latestIdSet: set, 当前帧中出现的id, 用于判断那些id没有被更新, 从而不参与算法计算。
    lastTimestamp: int, 当前帧的时间戳

    将当前帧数据添加到历史帧数据中, 同时重置时间戳, 保证时间戳恒增。进行原地修改。
    """
    # time1 = time.time()
    # 当前帧没有目标, 传来空数据, 直接返回
    if len(currentFrame) == 0:
        return set(), lastTimestamp
    # 如果不为第0帧, 已有历史数据
    if contextFrames:
        latestIdSet = set()
        for guid, objInfo in currentFrame.items():
            # 记录最新帧出现的目标id
            latestIdSet.add(guid)
            objInfo["timestamp"] = objInfo["secMark"]
            # while objInfo["timestamp"] < lastTimestamp:
            #     objInfo["timestamp"] += MaxSecMark
            # 将while改为直接计算
            objInfo["timestamp"] += MaxSecMark * (
                (lastTimestamp - objInfo["timestamp"]) // MaxSecMark + 1
            )
            contextFrames.setdefault(guid, [])
            if (
                len(contextFrames[guid])
                and contextFrames[guid][-1]["timestamp"]
                == objInfo["timestamp"]
            ):
                contextFrames[guid][-1] = objInfo
            else:
                contextFrames[guid].append(objInfo)
            current_secMark = objInfo["timestamp"]
        lastTimestamp = current_secMark
        # time2 = time.time()
        frameDelete(contextFrames, lastTimestamp)
        # time3 = time.time()
        # duration1 = time2 - time1
        # duration2 = time3 - time2
        # # 输出ms
        # print(f"framesCombination duration1: {duration1 * 1000:.3f} ms, \
        #     duration2: {duration2 * 1000:.3f} ms", end='\r')
        return latestIdSet, lastTimestamp
    # 如果历史数据为空, 即第0帧, 直接添加
    latestIdSet = set()
    for guid, objInfo in currentFrame.items():
        lastTimestamp = objInfo["timestamp"] = objInfo["secMark"]
        contextFrames[guid] = [objInfo]
        latestIdSet.add(guid)
    return latestIdSet, lastTimestamp


def getCurrentFrame(frames: dict, lastTimestamp: int) -> dict:
    """function getCurrentFrame

    input
    -----
    frames: dict, 历史帧数据(包含当前最新帧)
    lastTimestamp: int, 上一帧的时间戳

    output
    ------
    latestFrame: dict, 当前帧数据

    从历史帧数据中提取出当前帧数据。
    """
    latestFrame = {}
    for objInfo in frames.values():
        if objInfo[-1]["timestamp"] == lastTimestamp:
            obj_id = objInfo[-1]["id"]
            latestFrame[obj_id] = objInfo[-1]
    return latestFrame
