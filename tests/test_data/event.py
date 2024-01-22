events = {
    'spill': {
        'name': 'spill',
        'occured': True,
        'items': 
        {
            'A0000010':
            {
                'type': 'spill',
                'eventID': 'A0000010',
                'time': 200,
                'laneID': 5, 
                'order': 2,
                'start': 100,
                'end': 150,
                'danger': 1.002
            }
        }
        },
    'stop': {
        'name': 'stop',
        'occured': False,
        'items': {}
        },
    'lowSpeed': {
        'name': 'lowSpeed',
        'occured': False,
        'items': {}
        },
    'highSpeed': 
    {
        'name': 'highSpeed',
        'occured': True,
        'items':
        {
            'D0000340':
            {
                'type': 'highSpeed',
                'eventID': 'D0000340',
                'time': 234,
                'carID': 5800,
                'laneID': 5, 
                'x': 14.94,
                'y': 228.8,
                'vx': -0.72,
                'vy': 29.09,
                'speed': 29.098908914253126,
                'a': 0
            }
        }
    },
    'emgcBrake': {
        'name': 'emgcBrake',
        'occured': False,
        'items': {}
        },
    'incident': {
        'name': 'incident',
        'occured': True,
        'items': 
        {
            'F0000010':
            {
                'type': 'incident',
                'eventID': 'F0000010',
                'time': 200,
                'carID1': 5800,
                'carID2': 5801,
                'laneID1': 5,
                'laneID2': 5,
                'x1': 14.94,
                'y1': 228.8,
                'x2': 14.94,
                'y2': 228.8,
                'vx1': -0.72,
                'vy1': 1.09,
                'vx2': -0.77,
                'vy2': 0.09,
                'speed1': 1.5,
                'speed2': 1.6,
                'a1': 0,
                'a2': 0
            }
        }
    },
    'crowd': {
        'name': 'crowd',
        'occured': True,
        'items': 
        {
            'G0000010':
            {
                'type': 'crowd',
                'eventID': 'G0000010',
                'time': 200,
                'laneID': 5,
                'q': 110,
                'k': 20,
                'v': 5.5
            }
        },
    },
    'illegalOccupation': {
        'name': 'illegalOccupation',
        'occured': False,
        'items': {}
        }
    }


outerEvents = [
    {
        'type': 'spill',
        'eventID': 'A0000010',
        'time': 200,
        'laneID': 5, 
        'order': 2,
        'start': 100,
        'end': 150,
        'danger': 1.002
    },
    {
        'type': 'highSpeed',
        'eventID': 'D0000340',
        'time': 234,
        'carID': 5800,
        'laneID': 5, 
        'x': 14.94,
        'y': 228.8,
        'vx': -0.72,
        'vy': 29.09,
        'speed': 29.098908914253126,
        'a': 0
    },
    {
        'type': 'incident',
        'eventID': 'F0000010',
        'time': 200,
        'carID1': 5800,
        'carID2': 5801,
        'laneID1': 5,
        'laneID2': 5,
        'x1': 14.94,
        'y1': 228.8,
        'x2': 14.94,
        'y2': 228.8,
        'vx1': -0.72,
        'vy1': 1.09,
        'vx2': -0.77,
        'vy2': 0.09,
        'speed1': 1.5,
        'speed2': 1.6,
        'a1': 0,
        'a2': 0
    },
    {
        'type': 'crowd',
        'eventID': 'G0000010',
        'time': 200,
        'laneID': 5,
        'q': 110,
        'k': 20,
        'v': 5.5
    }
]
