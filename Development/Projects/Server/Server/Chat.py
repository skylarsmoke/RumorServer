'''
Chat Class

Contains all chat logic pertainin to the chat object
'''

# imports
import SQLManager
from datetime import datetime

def generateChatKey():
    db = SQLManager.SQLManager()
    SQL = "SELECT MAX(ChatKey) as ChatKey from tblChat"
    chatKey = db.select(SQL)
    
    for record in chatKey:
        if record.ChatKey == None:
            return 1
        return record.ChatKey + 1

def generateNewChat(Chat):
    Chat.ChatKey = generateChatKey()
    
    # insert new chat into database
    db = SQLManager.SQLManager()
    SQL = "INSERT INTO tblChat VALUES (?,?,?),(?,?,?)"
    createdDate = datetime.today().strftime('%Y-%m-%d')
    commaListVariables = f"{Chat.User1},{Chat.ChatKey},{createdDate},{Chat.User2},{Chat.ChatKey},{createdDate}"
    db.insert(SQL, commaListVariables)

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
            
    def isChatUser(self, userID):
        if self.User1 == userID or self.User2 == userID:
            return True
        else:
            return False