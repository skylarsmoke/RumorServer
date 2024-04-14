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
    def addPing(self, userID, ChatKeys, MsgKeys):
        
        # generate ping ID
        pingID = str(uuid.uuid4())

        # add ping to active ping list
        self.activePings.append([userID, pingID])
        
        # add chat/msg keys to dictionary with ping ID
        self.pingData[pingID] = ChatKeys + ":" + MsgKeys
        
        # return the pingID
        return pingID
        
    # returns the number of active pings
    def activePingCount(self):
        return len(self.activePings)

    # removes a ping from the list
    def removePing(self, userID, pingID):
        
        # first get the ping transfer data
        transferData = self.pingData[pingID]
        allKeys = transferData.split(':')
        if (allKeys[0] != ""):
            chatCount = allKeys[0].count(",") + 1
        else:
            chatCount = 0
            
        if (allKeys[1] != ""):
            msgCount = allKeys[1].count(",") + 1
        else:
            msgCount = 0

        # mark ping data as transferred
        db = SQLManager.SQLManager()
        
        # chat data
        inParameterHolder = ""
        if (chatCount > 0):
            inParameterHolder = ",".join("?" * chatCount)
            SQL = f"UPDATE tblChat SET Transmitted = 1 WHERE UserID = ? AND ChatKey IN ({inParameterHolder})"
            db.update(SQL, str(userID) + "," + allKeys[0])

        # msg data
        if (msgCount > 0):    
            inParameterHolder = ",".join("?" * msgCount)
            SQL = f"UPDATE tblMessageLog SET Transmitted = 1 WHERE MsgKey IN ({inParameterHolder})"
            db.update(SQL, allKeys[1])
        
        self.activePings.remove([userID, pingID])
