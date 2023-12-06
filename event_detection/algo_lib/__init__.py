from crowd import crowd_detect
from high_speed import high_speed_detect
from illegal_occupation import illegal_occupation_detect
from incident_single_car import incident_single_car_detect
from incident import incident_detect
from intensive_speed_reduction import intensive_speed_reduction_detect
from low_speed import low_speed_detect
from spill import spill_detect


# # 使得能够直接调用各函数

# def crowd_detect(msg, traffic, config, param):
#     return crowd_detect(msg, traffic, config, param)

# def high_speed_detect(msg, traffic, config, param):
#     return high_speed_detect(msg, traffic, config, param)

# def illegal_occupation_detect(msg, traffic, config, param):
#     return illegal_occupation_detect(msg, traffic, config, param)

# def incident_single_car_detect(msg, traffic, config, param):
#     return incident_single_car_detect(msg, traffic, config, param)

# def incident_detect(msg, traffic, config, param):
#     return incident_detect(msg, traffic, config, param):

# def intensive_speed_reduction_detect(msg, traffic, config, param):
#     return intensive_speed_reduction_detect(msg, traffic, config, param)

# def low_speed_detect(msg, traffic, config, param):
#     return low_speed_detect(msg, traffic, config, param)

# def spill_detect(msg, traffic, config, param):
#     return spill_detect(msg, traffic, config, param)