import math
import pre_processing.utils as utils


class Interpolation:
    """插值补全算法

    结构逻辑:
    1. 将历史帧数据与当前帧数据合并
    2. 根据延迟时间确定需要补全的时刻
    3. 根据缺失时刻前后轨迹速度判断是否合理
    4. 通过插值函数完成缺失轨迹点
    """

    def __init__(
        self,
        lagTime: int = 200,  # ms 至少保证雷达或视频可延时 1-2 帧
        maxSpeedMotor: int = 120,  # km/h
        maxSpeedNonMotor: int = 15,  # km/h
        maxSpeedPedestrian: int = 5,  # km/h
    ) -> None:
        """类初始化

        input
        -----
        lagTime: 为了获取缺失点前后轨迹所需的延迟时间
        maxSpeedMotor: 机动车最大允许补全点的速度
        maxSpeedNonMotor: 非机动车最大允许补全点的速度
        maxSpeedPedestrian: 行人最大允许补全点的速度
        """
        self._lagTime = lagTime   # 延误帧数
        self._speedCoefficient = 3.6
        # 若需补全的数据超过此时速, 则判为异常
        self._speedDict = {
            "motor": maxSpeedMotor / self._speedCoefficient,
            "non-motor": maxSpeedNonMotor / self._speedCoefficient,
            "pedestrian": maxSpeedPedestrian / self._speedCoefficient,
        }

    def run(
        self, contextFrames: dict, currentFrame: dict, lastTimestamp: int
    ) -> tuple:
        """外部调用函数

        input
        -----
        contextFrames: 算法的历史帧数据, 从上一次调用的结果中获得
        currentFrame: 最新的帧数据
        lastTimestamp: 上次调用算法函数时的当前帧数据时间戳

        output
        ------
        updatedLatestFrame: 完成处理后的最新帧数据
        lastTimestamp: 下次调用的当前帧数据的时间戳
        """
        _, lastTimestamp = utils.framesCombination(
            contextFrames, currentFrame, lastTimestamp
        )
        return (
            self._handleInterpolation(
                contextFrames, self._findDelaySecMark(contextFrames)
            ),
            lastTimestamp,
        )

    def _findNearest(self, array: list, value: int) -> int:
        # 找出需要做补全指定帧号下指定id的下标
        for index, j in enumerate(array):
            if j - value >= 0:
                return index
        return index

    def _isFrameValid(
        self, objInfo: dict, index: int, delaySecMark: int
    ) -> bool:
        if objInfo[index]["timeStamp"] <= delaySecMark:
            return False
        # 判断id下一次再出现时是否是位移过远, 是否是无效数据
        disX = objInfo[index]["x"] - objInfo[index - 1]["x"]
        disY = objInfo[index]["y"] - objInfo[index - 1]["y"]
        # 1000 用于毫秒转秒, 计算速度
        timeInterval = (
            objInfo[index]["timeStamp"] - objInfo[index - 1]["timeStamp"]
        ) / 1000
        speed = math.hypot(disX, disY) / timeInterval
        speedMax = self._speedDict[objInfo[index]["ptcType"]]
        return speedMax > speed

    def _complete_obj(
        self, objsInfo: list, index: int, delaySecMark: int
    ) -> None:
        # 补全指定的帧号下指定 id的轨迹点
        objsInfo.insert(index, objsInfo[index].copy())
        for i in ("x", "y"):
            objsInfo[index][i] = objsInfo[index - 1][i] + (
                objsInfo[index + 1][i] - objsInfo[index - 1][i]
            ) * (delaySecMark - objsInfo[index - 1]["timeStamp"]) / (
                objsInfo[index + 1]["timeStamp"]
                - objsInfo[index - 1]["timeStamp"]
            )
        objsInfo[index]["timeStamp"] = delaySecMark
        objsInfo[index]["secMark"] = delaySecMark % utils.MaxSecMark

    def _findDelaySecMark(self, frames: dict) -> int:
        # 找到 delaySecMark, 并更新原 frames的 secmark
        maxSec = 0
        for objsInfo in frames.values():
            maxSecEachId = objsInfo[-1]["timeStamp"]
            maxSec = max(maxSecEachId, maxSec)
        delaySecMark = maxSec
        for objsInfo in frames.values():
            for fr in objsInfo:
                if fr["timeStamp"] >= maxSec - self._lagTime:
                    delaySecMark = min(fr["timeStamp"], delaySecMark)
                    break
        return delaySecMark

    def _handleInterpolation(self, frames: dict, delaySecMark: int) -> dict:
        # 判断是否需要做补全, 并调相应函数做补全处理
        updatedLatestFrame = {}
        for objsInfo in frames.values():
            secMarkList = [fr["timeStamp"] for fr in objsInfo]
            index = self._findNearest(secMarkList, delaySecMark)
            if index != 0:
                if self._isFrameValid(objsInfo, index, delaySecMark):
                    self._complete_obj(objsInfo, index, delaySecMark)
                for i in range(len(objsInfo) - 1, -1, -1):
                    if objsInfo[i]["timeStamp"] == delaySecMark:
                        obj_id = objsInfo[i]["id"]
                        updatedLatestFrame[obj_id] = objsInfo[i]
        return updatedLatestFrame
