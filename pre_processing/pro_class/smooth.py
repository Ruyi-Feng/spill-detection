from pre_processing.utils import *

'''Define the smooth algorithm class.'''

class Exponential:
    """一次指数平滑算法
    
    1. 合并历史帧数据与当前帧数据
    2. 找到参与者上一帧的轨迹
    3. 通过指数平滑函数对最新轨迹点进行平滑
    """

    def __init__(
        self, smoothAlpha: float = 0.8, smooth_threshold: float = 2 * 1000
    ) -> None:
        """Class initialization.

        input
        -----
        smoothAlpha: 平滑系数
        smooth_threshold: 可用于平滑的轨迹点的时间阈值

        """
        self._smooth_threshold = smooth_threshold
        # The parameter of the smoothing formula
        self._smoothAlpha = smoothAlpha

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> (dict, any | int):
        """External call function.

        input
        -----
        context_frames: 算法的历史帧数据, 从上一次调用的结果中获得
        current_frame: 最新的帧数据
        last_timestamp: 上次调用算法函数时的当前帧数据时间戳

        output
        ------
        updated_latest_frame: 平滑处理后的最新帧数据
        last_timestamp:用于下次调用的当前帧数据的时间戳
        """
        # 将历史数据与最新帧数据合并
        latest_id_set, last_timestamp = frames_combination(
            context_frames, current_frame, last_timestamp
        )
        for obj_info in context_frames.values():
            self._smooth_one(obj_info, latest_id_set)
        return (
            get_current_frame(context_frames, last_timestamp),
            last_timestamp,
        )

    def _smooth_one(self, obj_info: list, latest_id_set: set) -> list:
        try:
            current = obj_info[-1]
        except IndexError:
            return obj_info
        if any(
            [
                obj_info[-1]["id"] not in latest_id_set,
                len(obj_info) == 1,
            ]
        ):
            return obj_info
        last = obj_info[-2]
        delta_time = current["timeStamp"] - last["timeStamp"]
        if delta_time > self._smooth_threshold:
            return obj_info
        for j in ("x", "y"):
            current[j] = current[j] * self._smoothAlpha + last[j] * (
                1 - self._smoothAlpha
            )
        return obj_info
