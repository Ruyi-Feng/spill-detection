'''Simulate 2 cars touches.'''


dataIncident = [
    [
        {'id': 1, 'x': 2.36, 'y': 25, 'vx': 0.13, 'vy': 20,
         'laneID': 4, 'ax': 0, 'ay': 10, 'a': 10, 'timestamp': 0, 'speed': 20,
         'latitude': 0, 'longitude': 0},
        {'id': 2, 'x': 2.36, 'y': 26, 'vx': 0.13, 'vy': 20,
         'laneID': 4, 'ax': 0, 'ay': 10, 'a': 10, 'timestamp': 0, 'speed': 20,
         'latitude': 0, 'longitude': 0},
    ],
    [
        {'id': 1, 'x': 2.36, 'y': 26, 'vx': 0, 'vy': 0,
         'laneID': 4, 'ax': 0, 'ay': 10, 'a': 10, 'timestamp': 0, 'speed': 20,
         'latitude': 0, 'longitude': 0},
        {'id': 2, 'x': 2.36, 'y': 26.5, 'vx': 0, 'vy': 0,
         'laneID': 4, 'ax': 0, 'ay': 10, 'a': 10, 'timestamp': 0, 'speed': 20,
         'latitude': 0, 'longitude': 0},
    ]
]

dataIncidentEvent = {
    'name': 'incident',
    'occured': True,
    'items':
    {
        'F0000000':
        {
            'type': 'incident',
            'eventID': 'F0000000',
            'startTime': 0,
            'endTime': 0,
            'carID1': 1,
            'carID2': 2,
            'laneID1': 4,
            'laneID2': 4,
            'x1': 2.36,
            'y1': 26,
            'x2': 2.36,
            'y2': 26.5,
            'vx1': 0,
            'vy1': 0,
            'vx2': 0,
            'vy2': 0,
            'speed1': 20,
            'speed2': 20,
            'a1': 10,
            'a2': 10,
            'lat': 0,
            'lon': 0
        }
    }
}
