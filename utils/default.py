'''define default event types.'''
defaultEventTypes = ["spill", "stop", "lowSpeed", "highSpeed",
                     "emgcBrake", "incident", "crowd", "illegalOccupation"]
typeIdDict = {defaultEventTypes[i]: i for i in
              range(len(defaultEventTypes))}
typeCharDict = {defaultEventTypes[i]: chr(i+65) for i in
                range(len(defaultEventTypes))}
CharTypeDict = {chr(i+65): defaultEventTypes[i] for i in
                range(len(defaultEventTypes))}