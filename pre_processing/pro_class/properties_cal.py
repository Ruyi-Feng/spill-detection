import math


class PropCalculator:
    '''class PropCalculator

    用于计算车辆目标的新增属性, 包括: 
    1. 车辆目标的加速度
    2. 车辆目标的速度值
    '''
    def __init__(self):
        pass

    def run(self, curTgt: list, lastTgt: list, cellLine: list) -> list:
        '''function run

        input
        -----
        curTgt: list
            当前帧车辆目标信息
        lastTgt: list
            上一帧车辆目标信息(用于计算加速度)

        return
        ------
        curTgt: list
            计算后的当前帧车辆目标信息

        '''
        resultTgt = []
        for tgt in curTgt:
            tgt = self.__run_acc(tgt, lastTgt)
            tgt = self.__run_speed(tgt)
            tgt = self.__run_cell(tgt, cellLine)
            resultTgt.append(tgt)

        return resultTgt

    def __run_acc(self, tgt: dict, lastTgt: list) -> dict:
        '''function __run_acc

        input
        -----
        tgt: dict
            当前帧车辆目标信息
        lastTgt: list
            上一帧车辆目标信息(用于计算加速度)
        return
        ------
        tgt: dict
            计算后的当前帧车辆目标信息

        '''
        return tgt

    def __run_speed(self, tgt: dict) -> dict:
        '''function __run_speed

        input
        -----
        tgt: dict
            当前帧车辆目标信息

        return
        ------
        tgt: dict
            计算后的当前帧车辆目标信息

        '''
        tgt['speed'] = math.sqrt(tgt['VDecVx']**2 + tgt['VDecVy']**2)
        return tgt
