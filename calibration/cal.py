import json
from sklearn.svm import SVC

class calibrator:
    '''
    生成标定器，用于标定检测区域的有效行驶片区和应急车道。
    '''
    def __init__(self):
        self.trafficTarget = {}
        self.laneTraffic = {}
        self.calibration = {}
        

    def recieve(self, msg):
        '''
        接受每帧传输来的目标信息，更新给calibrator
        '''
        self.trafficTarget[msg['frame']] = msg['target']    # TODO1
    
    def calibrate(self):
        self.calibration = {}

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.calibration, f)
