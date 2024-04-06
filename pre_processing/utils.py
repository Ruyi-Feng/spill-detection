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
