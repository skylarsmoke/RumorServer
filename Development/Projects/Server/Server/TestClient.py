'''
Test Client for testing Rumor server connectivity
'''

import socket

def execute():
    print("Initializing Test Client...")

    serverIP = 'localhost'
    serverPort = 5006
    buffer_size = 10
    clientID = "1 "

    # connect to server
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientMsg = clientID + input(">")
        
        client.sendto(clientMsg.encode('utf-8'), (serverIP, serverPort))
    

if __name__ == '__main__':
    execute()





