from pre_processing.utils import framesCombination, getCurrentFrame


'''Define the smooth algorithm class.'''


class Exponential:
    """一次指数平滑算法

    1. 合并历史帧数据与当前帧数据
    2. 找到参与者上一帧的轨迹
    3. 通过指数平滑函数对最新轨迹点进行平滑
    """

    def __init__(
        self, smoothAlpha: float = 0.8, smoothThreshold: float = 2 * 1000
    ) -> None:
        """Class initialization.

        input
        -----
        smoothAlpha: 平滑系数
        smoothThreshold: 可用于平滑的轨迹点的时间阈值

        """
        self._smoothThreshold = smoothThreshold
        # The parameter of the smoothing formula
        self._smoothAlpha = smoothAlpha

    def run(
        self, contextFrames: dict, currentFrame: dict, lastTimestamp: int
    ) -> (dict, int):
        """External call function.

        input
        -----
        contextFrames: 算法的历史帧数据, 从上一次调用的结果中获得
        currentFrame: 最新的帧数据
        lastTimestamp: 上次调用算法函数时的当前帧数据时间戳

        output
        ------
        updatedLatestFrame: 平滑处理后的最新帧数据
        lastTimestamp:用于下次调用的当前帧数据的时间戳
        """
        # 将历史数据与最新帧数据合并
        latestIdSet, lastTimestamp = framesCombination(
            contextFrames, currentFrame, lastTimestamp
        )
        for objInfo in contextFrames.values():
            self._smooth_one(objInfo, latestIdSet)
        return (
            getCurrentFrame(contextFrames, lastTimestamp),
            lastTimestamp,
        )

    def _smooth_one(self, objInfo: list, latestIdSet: set) -> list:
        try:
            current = objInfo[-1]
        except IndexError:
            return objInfo
        if any(
            [
                objInfo[-1]["id"] not in latestIdSet,
                len(objInfo) == 1,
            ]
        ):
            return objInfo
        last = objInfo[-2]
        deltaTime = current["timeStamp"] - last["timeStamp"]
        if deltaTime > self._smoothThreshold:
            return objInfo
        for j in ("x", "y"):
            current[j] = current[j] * self._smoothAlpha + last[j] * (
                1 - self._smoothAlpha
            )
        return objInfo
