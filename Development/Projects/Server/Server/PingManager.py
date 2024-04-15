'''
Contains the Ping class and manages all active Pings

'''

# imports
import SQLManager
import uuid

# ping object
class ping():
    
    def __init__(self):
        self.activePings = [[]]
        self.pingData = {}
        
    # adds a ping
    def addPing(self, userID, MsgKeys):
        
        # generate ping ID
        pingID = str(uuid.uuid4())

        # add ping to active ping list
        self.activePings.append([userID, pingID])
        
        # add chat/msg keys to dictionary with ping ID
        self.pingData[pingID] = MsgKeys
        
        # return the pingID
        return pingID
        
    # returns the number of active pings
    def activePingCount(self):
        return len(self.activePings)

    # removes a ping from the list
    def removePing(self, userID, pingID):
        
        # first get the ping transfer data
        MsgKeys = self.pingData[pingID]
        
        # check to see we have message keys before attempting to update database
        if (MsgKeys != ""):
            msgCount = MsgKeys.count(",") + 1
        else:
            msgCount = 0

        # mark ping data as transferred
        db = SQLManager.SQLManager()
        
        # TODO: Update index on tbllMessageLog to use MsgKey as the primary and reorder table columns

        # msg data
        if (msgCount > 0):    
            inParameterHolder = ",".join("?" * msgCount)
            SQL = f"UPDATE tblMessageLog SET Transmitted = 1 WHERE MsgKey IN ({inParameterHolder})"
            db.update(SQL, MsgKeys)
        
        self.activePings.remove([userID, pingID])
