import math
from pre_processing.uitls import (frame_delete, frames_combination,
                                  get_current_frame)


class Interpolation:
    """插值补全算法

    结构逻辑：
    1. 将历史帧数据与当前帧数据合并
    2. 根据延迟时间确定需要补全的时刻
    3. 根据缺失时刻前后轨迹速度判断是否合理
    4. 通过插值函数完成缺失轨迹点
    """

    def __init__(
        self,
        lag_time: int = 200,  # ms 至少保证雷达或视频可延时 1-2 帧
        max_speed_motor: int = 120,  # km/h
        max_speed_non_motor: int = 15,  # km/h
        max_speed_pedestrian: int = 5,  # km/h
    ) -> None:
        """类初始化

        input
        -----
        lag_time: 为了获取缺失点前后轨迹所需的延迟时间
        max_speed_motor: 机动车最大允许补全点的速度
        max_speed_non_motor: 非机动车最大允许补全点的速度
        max_speed_pedestrian: 行人最大允许补全点的速度
        """
        self._lag_time = lag_time
        # 延误帧数
        self._speed_coefficient = 3.6
        # 行人最大时速，若需补全的数据超过此时速，则判为异常
        self._speed_dict = {
            "motor": max_speed_motor / self._speed_coefficient,
            "non-motor": max_speed_non_motor / self._speed_coefficient,
            "pedestrian": max_speed_pedestrian / self._speed_coefficient,
        }

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """外部调用函数

        input
        -----
        context_frames: 算法的历史帧数据, 从上一次调用的结果中获得
        current_frame: 最新的帧数据
        last_timestamp: 上次调用算法函数时的当前帧数据时间戳

        output
        ------
        updated_latest_frame: 完成处理后的最新帧数据
        last_timestamp: 下次调用的当前帧数据的时间戳
        """
        _, last_timestamp = frames_combination(
            context_frames, current_frame, last_timestamp
        )
        return (
            self._handle_interpolation(
                context_frames, self._find_delay_sec_mark(context_frames)
            ),
            last_timestamp,
        )

    def _find_nearest(self, array: list, value: int) -> int:
        # 找出需要做补全指定帧号下指定id的下标
        for index, j in enumerate(array):
            if j - value >= 0:
                return index
        return index

    def _is_frame_valid(
        self, obj_info: dict, index: int, delay_sec_mark: int
    ) -> bool:
        if obj_info[index]["timeStamp"] <= delay_sec_mark:
            return False
        # 判断id下一次再出现时是否是位移过远，是否是无效数据
        dis_x = obj_info[index]["x"] - obj_info[index - 1]["x"]
        dis_y = obj_info[index]["y"] - obj_info[index - 1]["y"]
        # 1000 用于毫秒转秒，计算速度
        time_interval = (
            obj_info[index]["timeStamp"] - obj_info[index - 1]["timeStamp"]
        ) / 1000
        speed = math.hypot(dis_x, dis_y) / time_interval
        speed_max = self._speed_dict[obj_info[index]["ptcType"]]
        return speed_max > speed

    def _complete_obj(
        self, objs_info: list, index: int, delay_sec_mark: int
    ) -> None:
        # 补全指定的帧号下指定 id的轨迹点
        objs_info.insert(index, objs_info[index].copy())
        for i in ("x", "y"):
            objs_info[index][i] = objs_info[index - 1][i] + (
                objs_info[index + 1][i] - objs_info[index - 1][i]
            ) * (delay_sec_mark - objs_info[index - 1]["timeStamp"]) / (
                objs_info[index + 1]["timeStamp"]
                - objs_info[index - 1]["timeStamp"]
            )
        objs_info[index]["timeStamp"] = delay_sec_mark
        objs_info[index]["secMark"] = delay_sec_mark % utils.MaxSecMark

    def _find_delay_sec_mark(self, frames: dict) -> int:
        # 找到 delay_sec_mark，并更新原 frames的 secmark
        max_sec = 0
        for objs_info in frames.values():
            max_sec_each_id = objs_info[-1]["timeStamp"]
            max_sec = max(max_sec_each_id, max_sec)
        delay_sec_mark = max_sec
        for objs_info in frames.values():
            for fr in objs_info:
                if fr["timeStamp"] >= max_sec - self._lag_time:
                    delay_sec_mark = min(fr["timeStamp"], delay_sec_mark)
                    break
        return delay_sec_mark

    def _handle_interpolation(self, frames: dict, delay_sec_mark: int) -> dict:
        # 判断是否需要做补全，并调相应函数做补全处理
        updated_latest_frame = {}
        for objs_info in frames.values():
            sec_mark_list = [fr["timeStamp"] for fr in objs_info]
            index = self._find_nearest(sec_mark_list, delay_sec_mark)
            if index != 0:
                if self._is_frame_valid(objs_info, index, delay_sec_mark):
                    self._complete_obj(objs_info, index, delay_sec_mark)
                for i in range(len(objs_info) - 1, -1, -1):
                    if objs_info[i]["timeStamp"] == delay_sec_mark:
                        obj_id = objs_info[i]["global_track_id"]
                        updated_latest_frame[obj_id] = objs_info[i]
        return updated_latest_frame
