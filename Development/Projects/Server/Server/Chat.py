'''
Chat Class

Contains all chat logic pertainin to the chat object
'''

# imports
import SQLManager
from datetime import datetime

# generate chat key
def generateChatKey():
    db = SQLManager.SQLManager()
    SQL = "SELECT MAX(ChatKey) as ChatKey from tblChat"
    chatKey = db.select(SQL)
    
    for record in chatKey:
        if record.ChatKey == None:
            return 1
        return record.ChatKey + 1

# generates a new chat
def generateNewChat(Chat):
    Chat.ChatKey = generateChatKey()
    
    # insert new chat into database
    db = SQLManager.SQLManager()
    SQL = "INSERT INTO tblChat VALUES (?,?,?),(?,?,?)"
    createdDate = datetime.today().strftime('%Y-%m-%d')
    commaListVariables = f"{Chat.User1},{Chat.ChatKey},{createdDate},{Chat.User2},{Chat.ChatKey},{createdDate}"
    db.insert(SQL, commaListVariables)
    
# generates a msg key
def generateMsgKey(ChatKey):
    db = SQLManager.SQLManager()
    SQL = "SELECT MAX(MsgKey) AS MsgKey FROM tblMessageLog WHERE ChatKey = ?"
    msgKey = db.select(SQL, ChatKey)
    
    for record in msgKey:
        if record.MsgKey == None:
            return 1
        return record.MsgKey + 1
   
# stores messages in the database
def storeMsg(ChatKey, Message, UserTo, UserFrom):
    MsgKey = generateMsgKey(ChatKey)
    db = SQLManager.SQLManager()
    SQL = "INSERT INTO tblMessageLog VALUES (?,?,?,?,?,?)"
    dateSent = datetime.today().strftime('%Y-%m-%d')
    commaListVariables = f"{ChatKey},{MsgKey},{UserFrom},{UserTo},{Message},{dateSent}"
    db.insert(SQL, commaListVariables)
    return MsgKey

# Chat Object
class chat():

    def __init__(self, User1, User2, ChatKey = 0):
        
        # initialize variables
        self.User1 = User1
        self.User2 = User2
        self.ChatKey = ChatKey

        if self.ChatKey == 0:
            # this creates a new chat
            generateNewChat(self)
    
    # returns whether or not the UserID is in this chat
    def isChatUser(self, userID):
        if self.User1 == userID or self.User2 == userID:
            return True
        else:
            return False

    # handles logic to store and send messages to users
    def msg(self, UserTo, UserFrom, Message):
        # check if user from and to exist in chat
        if (UserTo != self.User1 and UserTo != self.User2):
            raise ValueError(f"User: {UserTo} does not exist in chat: {self.ChatKey}")
        
        if (UserFrom != self.User1 and UserFrom != self.User2):
            raise ValueError(f"User: {UserFrom} does not exist in chat: {self.ChatKey}")

        # when a message is created we store it first
        MsgKey = storeMsg(self.ChatKey, Message, UserTo, UserFrom)
        #sendMsg()
        
    # destructor
    def __del__(self):
        print("Chat: " + str(self.ChatKey) + " removed from cache")
        

