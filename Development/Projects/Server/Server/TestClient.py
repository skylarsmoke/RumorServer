'''
Test Client for testing Rumor server connectivity
'''
# b'gAAAAABl9qHKkdzKECWHeHlYKFoqG99kLgfIvbFV-e21UVbScwrSAihZBAL_0xnGArUyNsAtAfvrJryjGS8l3iSmtmankhwVNw=='
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
    print(clientID)

    # connect to server
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientMsg = clientID + input(">")
        
        client.sendto(clientMsg.encode('utf-8'), (serverIP, serverPort))
        
        if clientID == "0 ":
            received = str(client.recv(1024), "utf-8")
            fileWrite = open("user.txt", "w", encoding='utf-8')
            fileWrite.truncate()
            fileWrite.write("userID:" + received)
            fileWrite.close()
            clientID = received + " "
    

if __name__ == '__main__':
    execute()





