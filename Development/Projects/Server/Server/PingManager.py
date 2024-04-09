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
        pingID = uuid.uuid4()

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

        # mark ping data as transferred
        #db = SQLManager.SQLManager()
        

        self.activePings.remove([userID, pingID])
