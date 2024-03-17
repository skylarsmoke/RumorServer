'''
Rumor Server

Contains server side operations and hosts connections between users
'''

# imports
from asyncio.windows_events import NULL
from collections import UserList
from http import client
import uuid
import socketserver
import sys
from User import user
import Version
from timeit import default_timer
import Security
import SQLManager
import Encrypt


# Global Variables
userList = {}
serverIP = 'localhost'
serverPort = 5006
standbyTime = default_timer()
#key = Encrypt.Fernet.generate_key()

adminAccessDeniedMsg = "Admin access required to access command."

# returns the user object if client IP is found
def isUser(userID):
    if userID in userList:
        return userList[userID]
    else:
        return NULL
    
def deleteUserObjects():
    for user in userList:
        del user

# returns the current user object and creates a new one if one doesn't exist
def getUserObject(clientAddress, userID):
    userObject = isUser(userID)
    
    if userObject is NULL:
        global userNumber
        newUser = user(userID, clientAddress, 0)
        userList[userID] = newUser
        return newUser
    else:
        return userObject
    

# generates a unique user ID
def generateUserID():
    db = SQLManager.SQLManager()
    SQL = "select MAX(UserID) + 1 as NewUserID from tblUser"
    data = db.select(SQL)

    for record in data:
        if record.NewUserID == None:
            return 1
        return int(record.NewUserID)
    

def getUsername(currentUser):
    username = currentUser.username
    
    if username == "":
        return "Unknown User"
    else:
        return username

def getNumberOfCachedUsers():
    return len(userList)

def getUserID(msg):
    return int(msg[0:msg.find(" ")])

# sub class of UDP server
class UDPHandler(socketserver.DatagramRequestHandler):
    def setup(self):
        return super().setup()
    
    def handle(self):
        # once user is connected we must assign a user object to them
        clientMsg = self.request[0].decode('utf-8').strip();
        test = self.client_address

        # retrieve unique client ID
        userID = getUserID(clientMsg)
        if userID == 0:
            userID = generateUserID()
            self.request[1].sendto(str(userID).encode("utf-8"), self.client_address)
        
        # remove client ID from message
        clientMsg = clientMsg[clientMsg.find(" ") + 1:]

        currentUser = getUserObject(self.client_address[0], userID)
        username = getUsername(currentUser) # current users username
        
        # username command
        if (clientMsg.lower().startswith("@setusername")):
            currentUser.setUsername(clientMsg[clientMsg.find("username") + 9:])
            print(f"Username: {currentUser.username} saved for User ID: {currentUser.ID}")
        
        # ban command
        if (clientMsg.lower().startswith("@banuser") and currentUser.accessLevel == Security.adminAccess):
            print("Ban command under maintenance")
        elif (clientMsg.lower().startswith("@banuser")):
            print(adminAccessDeniedMsg)

        # get number of cached users command
        if (clientMsg.lower().startswith("@getusercount")):
            print(f"Number of cached user objects: {getNumberOfCachedUsers()}")

        # prints message from client, used for testing
        print(username + ": " + clientMsg)
        
        # reset global timer
        global standbyTime
        standbyTime = default_timer()
        
        
    def finish(self):
        return super().finish()

# starts server operations
def execute():
    
    print("Initializing " + Version.product + " Server - Version: " + Version.buildVersion)
    
    # Server connect logic
    with socketserver.UDPServer((serverIP, serverPort), UDPHandler) as server:
        print("Server Running...")
        
        try:
            server.serve_forever()
        except:
            print("Server shutting down...")
            if len(userList) > 0:
               print("Deleting user objects...")
               deleteUserObjects()
            print ("Shutdown Succesful")
            

if __name__ == "__main__":
    execute()