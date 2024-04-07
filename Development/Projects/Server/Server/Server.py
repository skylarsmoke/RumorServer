#!/usr/bin/env python3.9
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
from Chat import chat

# Global Variables
userList = {}
activeChats = {}
serverIP = 'localhost'
serverPort = 5006
standbyTime = default_timer()

adminAccessDeniedMsg = "Admin access required to access command."

# returns the user object if client ID is found
def isUser(userID):
    if userID in userList:
        return userList[userID]
    else:
        return NULL

# deletes all cached user objects
def deleteCachedUserObjects():
    for user in userList:
        del user
        
# deletes all cached chat objects
def deleteCachedChats():
    for chat in activeChats:
        del chat

# returns the current user object and creates a new one if one doesn't exist
def getUserObject(clientAddress, userID):
    userObject = isUser(userID)
    
    if userObject is NULL:
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
    
# gets users username
def getUsername(currentUser):
    username = currentUser.username
    
    if username == "":
        return "Unknown User"
    else:
        return username

# gets the number of cached users in the session
def getNumberOfCachedUsers():
    return len(userList)

def getNumberOfCachedChats():
    return len(activeChats)

# gets the user ID from the client msg
def getUserID(msg):
    return int(msg[0:msg.find(" ")])

# creates a new chat, returns the chat key
def createNewChat(userID1, userID2):
    chatObject = chat(userID1, userID2)
    activeChats[chatObject.ChatKey] = chatObject
    return chatObject.ChatKey

# checks if a user exists
def userExists(userID):
    db = SQLManager.SQLManager()
    SQL = "SELECT 1 as count from tblUser WHERE UserID = ?"
    results = db.select(SQL, userID)
    if len(results) == 0:
        return False
    else:
        return True
    
# check if a chat exists for a given chat key and userID
def chatExists(userID, ChatKey):
    db = SQLManager.SQLManager()
    SQL = "SELECT 1 AS count from tblChat WHERE UserID = ? AND ChatKey = ?"
    commaListVariables = f"{userID},{ChatKey}"
    results = db.select(SQL, commaListVariables)
    if len(results) == 0:
        return False
    else:
        return True

# retrieves a chat object from a given chat key
def getChatObject(ChatKey, User1, User2):
     if ChatKey in activeChats:
        return activeChats[ChatKey]
     else:
        chatObject = chat(User1, User2, ChatKey)
        activeChats[chatObject.ChatKey] = chatObject
        return chatObject

# sub class of UDP server
class UDPHandler(socketserver.DatagramRequestHandler):
    def setup(self):
        return super().setup()
    
    def handle(self):
        # once user is connected we must assign a user object to them
        clientMsg = self.request[0].decode('utf-8').strip();

        # retrieve unique client ID
        userID = getUserID(clientMsg)
        if userID == 0:
            userID = generateUserID()
            self.request[1].sendto(str(userID).encode("utf-8"), self.client_address)
        
        # remove client ID from message
        clientMsg = clientMsg[clientMsg.find(" ") + 1:]
        
        currentUser = getUserObject(self.client_address[0], userID)
        username = getUsername(currentUser) # current users username
        
        # check for new chat request
        if (clientMsg.lower().startswith("#newchat:")):
            userID2 = int(clientMsg[clientMsg.find(":") + 1:])
            
            # verify user2 exists
            if userExists(userID2):
                ChatKey = createNewChat(userID, userID2)
                self.request[1].sendto(("#chatkey:" + str(ChatKey)).encode("utf-8"), self.client_address)
            else:
                self.request[1].sendto("User does not exist.".encode("utf-8"), self.client_address)
         
        if (clientMsg.lower().startswith("#newmsg:")):
            # remove new msg clause
            msgParts = clientMsg.split(":")

            # get chatkey, userTo, and message
            ChatKey = int(msgParts[1])
            UserTo = int(msgParts[2])
            
            Message = msgParts[3]
            
            # verify chat exists
            if chatExists(userID, ChatKey):
                ChatObject = getChatObject(ChatKey, userID, UserTo)
                t = ChatObject.User1
                s = ChatObject.User2
                MsgKey = ChatObject.msg(UserTo, userID, Message)
                self.request[1].sendto(("#msgkey:" + str(MsgKey)).encode("utf-8"), self.client_address)
            else:
                self.request[1].sendto("Chat does not exist.".encode("utf-8"), self.client_address)

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
        
        # TODO: Multi thread to allow for periodic cache deletion
        try:
            server.serve_forever()
        except:
            print("Server shutting down...")
            if len(userList) > 0:
               print("Deleting cached user objects...")
               deleteCachedUserObjects()
               print("Deleting cached chat objects...")
               deleteCachedChats()
            print ("Shutdown Succesful")
            

if __name__ == "__main__":
    execute()