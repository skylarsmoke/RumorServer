#!/usr/bin/env python3.9
'''
Rumor Server

Contains server side operations and hosts connections between users
'''

# imports
from asyncio.windows_events import NULL
from collections import UserList
from http import client, server
import uuid
import socketserver
import sys
from User import initializeUserObject, user
import Version
import time
import Security
import SQLManager
import Encrypt
from Chat import chat
import threading
import json

# Global Variables
userList = {}
activeChats = {}
serverIP = 'localhost'
serverPort = 5006
serverRunning = True
currentUser = NULL

adminAccessDeniedMsg = "Admin access required to access command."

# returns the user object if client ID is found
def isUser(userID):
    if userID in userList:
        return userList[userID]
    else:
        return NULL

# deletes all cached user objects
def deleteCachedUserObjects():
    userList.clear()
        
# deletes all cached chat objects
def deleteCachedChats():
    activeChats.clear()

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

# retrieves chat data for ping response
def retrieveChatData(userID):
    db = SQLManager.SQLManager()
    SQL = "SELECT UserID, ChatKey, Created FROM tblChat WHERE UserID = ? AND Transmitted = 0"
    return db.selectPing(SQL, userID)

# retrieves msg data for ping response
def retrieveMsgData(ChatData):
    # first we grab the Chat keys
    ChatKeys = ""
    count = 0
    for item in ChatData:
        ChatKeys += str(item["ChatKey"]) + ","
        count += 1

    # remove last comma
    ChatKeys = ChatKeys.rstrip(',')    

    db = SQLManager.SQLManager()
    inParameterHolder = ",".join("?" * count)
    SQL = f"SELECT ChatKey, MsgKey, UserFrom, UserTo, Message, DateSent FROM tblMessageLog WHERE ChatKey IN ({inParameterHolder}) and Transmitted = 0" 
    return db.selectPing(SQL, ChatKeys)

# serializes the chat and msg data to JSON
def serializeData(ChatData, MsgData):
    serializedChat = json.dumps(ChatData, indent=4, sort_keys=True, default=str)
    serializedMsg = json.dumps(MsgData, indent=4, sort_keys=True, default=str)
    
    # we join together the serialized data separating them by a dollar sign
    return serializedChat + "$" + serializedMsg

def markDataAsTransmitted(UserID):
    print("") # TODO Mark data as transmitted to prevent duplicate transmission

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
        
        global currentUser
        currentUser = getUserObject(self.client_address[0], userID)
        username = getUsername(currentUser) # current users username

        if (clientMsg.lower() == "#pong"):
            markDataAsTransmitted(userID)

        # transmit message data to users requesting
        if (clientMsg.lower() == "#ping"):
            ChatData = retrieveChatData(userID)
            MsgData = retrieveMsgData(ChatData)
            
            # serialize and send data to user
            SerializedData = serializeData(ChatData, MsgData)
            
            self.request[1].sendto(SerializedData.encode("utf-8"), self.client_address)
        
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
                
    def finish(self):
        return super().finish()

# opens the UDP connection for clients to communicate back and forth with the server
def initializeServer():
    # Server connect logic
    with socketserver.UDPServer((serverIP, serverPort), UDPHandler) as server:
        print("Server Running...")
        
        try:
            server.serve_forever()
        except:
            global serverRunning
            serverRunning = False
            print("Server shutting down...")
            if len(userList) > 0:
               print("Deleting cached user objects...")
               deleteCachedUserObjects()
            
            if len(activeChats) > 0:
               print("Deleting cached chat objects...")
               deleteCachedChats()
               
            print ("Shutdown Succesful")
            
# maintains the server cache, deleting and refreshing objects as needed
def maintainCache():
    global serverRunning
    start = time.monotonic()
    while (serverRunning):
        time.sleep(300.0 - ((time.monotonic() - start) % 300.0))
        print("Deleting cache...")
        deleteCachedUserObjects()
        deleteCachedChats()
        

# starts server operations
def execute():
    
    print("Initializing " + Version.product + " Server - Version: " + Version.buildVersion)
    
    t1 = threading.Thread(target=initializeServer)
    t2 = threading.Thread(target=maintainCache)

    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    print("Thread shutdown successful")

    # main 
if __name__ == "__main__":
    execute()