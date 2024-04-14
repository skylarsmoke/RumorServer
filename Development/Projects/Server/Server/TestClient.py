#!/usr/bin/env python3.9
'''
Test Client for testing Rumor server connectivity
'''

import socket
import Encrypt

def execute():
    print("Initializing Test Client...")

    serverIP = 'localhost'
    serverPort = 5006
    buffer_size = 10

    userFile = open("user.txt", "r", encoding='utf-8') 
    clientID = userFile.read()
    userFile.close()
    
    # decrypt file
    clientID = clientID[1:]
    clientID = Encrypt.decrypt(clientID)
    clientID = clientID[clientID.find(":") + 1:] + " "

    # connect to server
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientMsg = clientID + input(">")
        
        client.sendto(clientMsg.encode('utf-8'), (serverIP, serverPort))
        
        if clientID == "0 ":
            received = str(client.recv(1024), "utf-8")
            fileWrite = open("user.txt", "w", encoding='utf-8')
            fileWrite.truncate()
            encryptedUserID = Encrypt.encrypt("userID:" + received)
            fileWrite.write("\'" + encryptedUserID.decode("utf-8") + "\'")
            fileWrite.close()
            clientID = received + " "
            
        if (clientMsg.startswith(clientID + "#newchat:")):
            received = str(client.recv(1024), "utf-8")
            print("ChatKey: " + received)
            
        if (clientMsg.startswith(clientID + "#ping")):
            received = str(client.recv(10000), "utf-8")
            
            # send acknowledgement of receipt
            client.sendto((clientID + "#pong:" + received[:received.find("*")]).encode("utf-8"), (serverIP, serverPort))
    

if __name__ == '__main__':
    execute()





