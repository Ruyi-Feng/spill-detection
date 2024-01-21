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


def carsList2Dict(cars: list) -> dict:
    '''function carsList2Dict

    input
    ------
    cars: list, 传感器数据

    output
    ------
    carsDict: dict, id为键, 单车数据为值的字典

    将传感器数据按id组织为字典。
    当前项目中, 仅用于prepro, 由于其他模块已经定型处理list, 故不使用本函数。
    '''
    carsDict = {}
    for car in cars:
        carsDict[car['id']] = car
    return carsDict


def carsDict2List(cars: dict) -> list:
    '''function _carsDict2List

    input
    ------
    cars: dict, id为键, 单车数据为值的字典

    output
    ------
    cars: list, 传感器数据

    将传感器数据由字典转换为列表。
    当前项目中, 仅用于prepro, 由于其他模块已经定型处理list, 故不使用本函数。
    '''
    carsList = []
    for car in cars.values():
        carsList.append(car)
    return carsList


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
    info = f"位置(x,y): {round(car['x'], 0)}m, {round(car['y'], 0)}m, " + \
        f"车道号: {car['laneID']}, " + \
        "速度(vx,vy,speed): " + \
        str(round(car['vx'] * 3.6, 0)) + ", " + \
        str(round(car['vy'] * 3.6, 0)) + ", " + \
        str(round(car['speed'] * 3.6, 0)) + "km/h "
    return info
