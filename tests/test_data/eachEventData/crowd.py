from datetime import datetime


eventID = datetime.now().strftime('%Y%m%d') + '-G00001'
dataCrowdEvent = {
    'name': 'crowd',
    'occured': True,
    'items':
    {
        eventID:
        {
            'type': 'crowd',
            'eventID': eventID,
            'startTime': 200,
            'endTime': -1,
            'laneID': 3,
            'q': 0,
            'k': 30,
            'v': 3,
            'lat': 3,
            'lon': 0,
            'deviceID': 'K68+366',
            'deviceType': '1',
            'rawClass': -1
        }
    }
}
