'''Define common functions for car data processing.'''


def getCarFromCars(cars: list, id: int) -> dict:
    '''function _getCarFromCars

    input
    ------
    cars: list, 传感器数据
    id: int, 车辆id

    output
    ------
    car: dict, 单车数据

    从传感器数据中获取指定id的单车数据。
    '''
    for car in cars:
        if car['id'] == id:
            return car  # 找到指定id的车辆
    return None     # 未找到指定id的车辆


def getCarBaseInfo(car: dict) -> str:
    '''function _getCarBaseInfo

    input
    ------
    car: dict, 单车数据

    return
    ------
    info: str, 单车基本信息字符串

    获取单车基本信息字符串, 用于事件信息输出。
    基本信息包括x,y,laneID,vx,vy。
    '''
    info = f"(x,y)=[{round(car['x'], 0)}, {round(car['y'], 0)}]m, " + \
        f"lane={car['laneID']}, " + \
        "(vx,vy,speed)=[" + \
        str(round(car['vx'] * 3.6, 0)) + ", " + \
        str(round(car['vy'] * 3.6, 0)) + ", " + \
        str(round(car['speed'] * 3.6, 0)) + "]km/h "
    return info
