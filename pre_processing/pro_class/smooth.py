'''Define the smooth algorithm class.'''

class Exponential:
    """一次指数平滑算法
    
    1. 合并历史帧数据与当前帧数据
    2. 找到参与者上一帧的轨迹
    3. 通过指数平滑函数对最新轨迹点进行平滑
    """

    def __init__(
        self, smooth_index: float = 0.8, smooth_threshold: float = 2 * 1000
    ) -> None:
        """Class initialization.

        smooth_index:
        The parameter of the smoothing formula

        smooth_threshold:
        Time threshold of trajectory points that can be used for smoothing

        """
        self._smooth_threshold = smooth_threshold
        # The parameter of the smoothing formula
        self._smooth_index = smooth_index

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function.

        Input:
        context_frames:
        Algorithm's historical frame data, obtained from the result of the last
        call, AID format

        current_frame:
        latest frame data, AID format

        last_timestamp:
        The current frame data timestamp when the algorithm function was last
        called

        Output:
        updated_latest_frame:
        The latest frame data after smooth processing, AID format

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        # 将历史数据与最新帧数据合并
        latest_id_set, last_timestamp = utils.frames_combination(
            context_frames, current_frame, last_timestamp
        )
        for obj_info in context_frames.values():
            self._smooth_one(obj_info, latest_id_set)
        return (
            utils.get_current_frame(context_frames, last_timestamp),
            last_timestamp,
        )

    def _smooth_one(self, obj_info: list, latest_id_set: set) -> list:
        try:
            current = obj_info[-1]
        except IndexError:
            return obj_info
        if any(
            [
                obj_info[-1]["global_track_id"] not in latest_id_set,
                len(obj_info) == 1,
            ]
        ):
            return obj_info
        last = obj_info[-2]
        delta_time = current["timeStamp"] - last["timeStamp"]
        if delta_time > self._smooth_threshold:
            return obj_info
        for j in ("x", "y"):
            current[j] = current[j] * self._smooth_index + last[j] * (
                1 - self._smooth_index
            )
        return obj_info