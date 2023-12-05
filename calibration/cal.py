import json

class calibrator:
    '''
    生成标定器，用于标定检测区域的有效行驶片区和应急车道。
    '''
    def __init__(self):
        self.traffic = False
        self.calibration = {}

    def recieve(self, msg):
        self.data = msg
        
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.calibration, f)
