# import math
import pre_processing.utils as utils
import time

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
        # self._speedDict = {
        #     "motor": maxSpeedMotor / self._speedCoefficient,
        #     "non-motor": maxSpeedNonMotor / self._speedCoefficient,
        #     "pedestrian": maxSpeedPedestrian / self._speedCoefficient,
        # }
        self.count = 0   # 记录用于报告时长
        # 时长记录列表
        self.timeList = [[] for _ in range(5)]

    def run(
        self, contextFrames: dict, currentFrame: dict, lastTimestamp: int
    ) -> tuple:
        """外部调用函数
        input
        -----
        contextFrames: 算法的历史帧数据, 从上一次调用的结果中获得,
                       以id为索引, 值为以时间戳为索引的dict
        currentFrame: 最新的帧数据
        lastTimestamp: 上次调用算法函数时的当前帧数据时间戳

        output
        ------
        updatedLatestFrame: 完成处理后的最新帧数据
        lastTimestamp: 下次调用的当前帧数据的时间戳
        """
        self.count += 1
        # 获取设备名称
        key = list(currentFrame.keys())[0]
        self.deviceID = currentFrame[key]["deviceID"]
        if self.count % 2400 == 0:
            self.reportRuntime()
        time1 = time.time()
        # if self.count > 6000:
        #     print(f'count is {self.count}')
        _, lastTimestamp = utils.framesCombination(
            contextFrames, currentFrame, lastTimestamp
        )
        time2 = time.time()
        self.timeList[0].append(time2 - time1)
        return (
            self._handleInterpolation(
                contextFrames, self._findDelaySecMark(contextFrames)
            ),
            lastTimestamp,
        )

    def _findNearest(self, array: list, value: int) -> int:
        time1 = time.time()
        # 找出需要做补全指定帧号下指定id的下标
        for index, j in enumerate(array):
            if j - value >= 0:
                return index
        time2 = time.time()
        self.timeList[3].append(time2 - time1)
        return index

    def _isFrameValid(
        self, objInfo: dict, index: int, delaySecMark: int
    ) -> bool:
        if objInfo[index]["timestamp"] <= delaySecMark:
            return False
        return True
        """
        # 判断id下一次再出现时是否是位移过远, 是否是无效数据
        disX = objInfo[index]["x"] - objInfo[index - 1]["x"]
        disY = objInfo[index]["y"] - objInfo[index - 1]["y"]
        # 1000 用于毫秒转秒, 计算速度
        timeInterval = (
            objInfo[index]["timestamp"] - objInfo[index - 1]["timestamp"]
        ) / 1000
        speed = math.hypot(disX, disY) / timeInterval
        speedMax = self._speedDict[objInfo[index]["ptcType"]]
        return speedMax > speed
        """

    def _complete_obj(
        self, objsInfo: list, index: int, delaySecMark: int
    ) -> None:
        time1 = time.time()
        # 补全指定的帧号下指定 id的轨迹点
        objsInfo.insert(index, objsInfo[index].copy())
        for i in ("x", "y"):
            objsInfo[index][i] = objsInfo[index - 1][i] + (
                objsInfo[index + 1][i] - objsInfo[index - 1][i]
            ) * (delaySecMark - objsInfo[index - 1]["timestamp"]) / (
                objsInfo[index + 1]["timestamp"]
                - objsInfo[index - 1]["timestamp"]
            )
        objsInfo[index]["timestamp"] = delaySecMark
        objsInfo[index]["secMark"] = delaySecMark % utils.MaxSecMark
        time2 = time.time()
        self.timeList[4].append(time2 - time1)

    def _findDelaySecMark(self, frames: dict) -> int:
        # 找到 delaySecMark, 并更新原 frames的 secmark
        time1 = time.time()
        maxSec = 0
        for objsInfo in frames.values():
            maxSecEachId = objsInfo[-1]["timestamp"]
            maxSec = max(maxSecEachId, maxSec)
        delaySecMark = maxSec
        for objsInfo in frames.values():
            for fr in objsInfo:
                if fr["timestamp"] >= maxSec - self._lagTime:
                    delaySecMark = min(fr["timestamp"], delaySecMark)
                    break
        time2 = time.time()
        self.timeList[1].append(time2 - time1)
        return delaySecMark

    def _handleInterpolation(self, frames: dict, delaySecMark: int) -> dict:
        # 判断是否需要做补全, 并调相应函数做补全处理
        time1 = time.time()
        updatedLatestFrame = {}
        for objsInfo in frames.values():
            secMarkList = [fr["timestamp"] for fr in objsInfo]
            index = self._findNearest(secMarkList, delaySecMark)
            if index != 0:
                if self._isFrameValid(objsInfo, index, delaySecMark):
                    self._complete_obj(objsInfo, index, delaySecMark)
                # for i in range(len(objsInfo) - 1, -1, -1):
                #     if objsInfo[i]["timestamp"] == delaySecMark:
                #         obj_id = objsInfo[i]["id"]
                #         updatedLatestFrame[obj_id] = objsInfo[i]
                # 将该遍历修正为无需遍历的操作
                obj_id = objsInfo[index]["id"]
                updatedLatestFrame[obj_id] = objsInfo[index]
                # 或者这样呢？
                # targetedObj = [obj for obj in objsInfo if obj["timestamp"] == delaySecMark][0]
                # updatedLatestFrame[targetedObj["id"]] = targetedObj
        time2 = time.time()
        self.timeList[2].append(time2 - time1)
        return updatedLatestFrame

    def reportRuntime(self):
        '''func reportRuntime
        
        输出算法运行时长
        '''
        # 计算各阶段
        totalTimeCombination = sum(self.timeList[0])
        totalTimeFindDelay = sum(self.timeList[1])
        totalTimeHandleInterpolation = sum(self.timeList[2])
        totalTimeFindNearest = sum(self.timeList[3])
        totalTimeCompleteObj = sum(self.timeList[4])
        totalTimeAll = totalTimeCombination + totalTimeFindDelay + \
            totalTimeHandleInterpolation
        # 计算平均每次计算的平均时长
        avgTimeCombination = totalTimeCombination / self.count
        avgTimeFindDelay = totalTimeFindDelay / self.count
        avgTimeHandleInterpolation = totalTimeHandleInterpolation / self.count
        avgTimeFindNearest = totalTimeFindNearest / self.count
        avgTimeCompleteObj = totalTimeCompleteObj / self.count
        avgTimeAll = totalTimeAll / self.count
        # 计算各阶段耗时占总时长的比例
        ratioCombination = totalTimeCombination / totalTimeAll
        ratioFindDelay = totalTimeFindDelay / totalTimeAll
        ratioHandleInterpolation = totalTimeHandleInterpolation / totalTimeAll
        ratioTimeFindNearest = totalTimeFindNearest / totalTimeAll
        ratioCompleteObj = totalTimeCompleteObj / totalTimeAll
        # 输出报告，单位ms
        print('Interpolation report:')
        print('deviceID', self.deviceID, 'count:', self.count)
        print(f'总耗时：{totalTimeAll*1000:.2f}ms, 平均每次耗时：{avgTimeAll*1000:.2f}ms')
        print(f'合并历史帧数据耗时：{totalTimeCombination*1000:.2f}ms, 平均每次耗时：{avgTimeCombination*1000:.2f}ms, 占比：{ratioCombination:.2%}')
        print(f'查找延迟帧号耗时：{totalTimeFindDelay*1000:.2f}ms, 平均每次耗时：{avgTimeFindDelay*1000:.2f}ms, 占比：{ratioFindDelay:.2%}')
        print(f'处理插值耗时：{totalTimeHandleInterpolation*1000:.2f}ms, 平均每次耗时：{avgTimeHandleInterpolation*1000:.2f}ms, 占比：{ratioHandleInterpolation:.2%}')
        print(f'查找最近帧号耗时：{totalTimeFindNearest*1000:.2f}ms, 平均每次耗时：{avgTimeFindNearest*1000:.2f}ms, 占比：{ratioTimeFindNearest:.2%}')
        print(f'补全轨迹点耗时：{totalTimeCompleteObj*1000:.2f}ms, 平均每次耗时：{avgTimeCompleteObj*1000:.2f}ms, 占比：{ratioCompleteObj:.2%}')
        # # count重置0
        # self.count = 0
        # self.timeList = [[] for _ in range(5)]
