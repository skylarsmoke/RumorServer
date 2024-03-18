'''
User Class

Contains all logic and attributes pertaining to user instances
'''

# imports
from datetime import datetime
import Security
import SQLManager

# retrieves user info
def getUserInfo(userID):
    # attempt to find user info in database
    db = SQLManager.SQLManager()
    SQL = "SELECT * from tblUser where UserID = ?"
    return db.select(SQL, userID)

# initializes user object
def initializeUserObject(userObject):
    userInfo = getUserInfo(userObject.ID)
    if len(userInfo) > 1:
        raise ValueError("More than one user returned.")

    # grabs data pulled back from database, uses column names from tblUser
    for record in userInfo:
        userObject.accessLevel = record.AccessLevel
        userObject.banned = record.Banned
        userObject.username = record.Username
        return True
    
    # user does not exist, so we insert new user record
    return False

# stores new user info
def insertNewUserRecord(userObject):
    db = SQLManager.SQLManager()
    SQL = "INSERT INTO tblUser VALUES (?,?,?,?,?,?,?)"
    commaListVariables = f"{userObject.ID},{userObject.username},{userObject.IP},{userObject.Port},{userObject.accessLevel},{1 if userObject.banned == True else 0},{userObject.lastLogin}"
    db.insert(SQL, commaListVariables)

# user object
class user():

    username = "";
    banned = False
    
    def __init__(self, userID, clientIP, port):
        self.ID = userID
        self.IP = clientIP
        self.Port = port
        self.lastLogin = datetime.today().strftime('%Y-%m-%d')

        # initialize user object data
        if not initializeUserObject(self):
            self.accessLevel = Security.userAccess
            insertNewUserRecord(self)
        
    # sets users username and commits it to the database
    def setUsername(self, username):
        self.username = username
        db = SQLManager.SQLManager()
        SQL = "UPDATE tblUser SET Username = ? WHERE UserID = ?"
        commaListVariable = f"{self.username},{self.ID}"
        db.update(SQL, commaListVariable)

    # sets user to be have admine access
    def setAdmin(self):
        self.accessLevel = Security.adminAccess
        db = SQLManager.SQLManager()
        SQL = "UPDATE tblUser SET AccessLevel = ? WHERE UserID = ?"
        commaListVariable = f"{self.accessLevel},{self.ID}"
        db.update(SQL, commaListVariable)

    # bans the user
    def banUser(self):
        self.banned = True
        db = SQLManager.SQLManager()
        SQL = "UPDATE tblUser SET Banned = ? WHERE UserID = ?"
        commaListVariable = f"{self.banned},{self.ID}"
        db.update(SQL, commaListVariable)

    # unbans the user
    def unbanUser(self):
        self.banned = False
        db = SQLManager.SQLManager()
        SQL = "UPDATE tblUser SET Banned = ? WHERE UserID = ?"
        commaListVariable = f"{self.banned},{self.ID}"
        db.update(SQL, commaListVariable)

    # destructor
    def __del__(self):
        print("User: " + str(self.ID) + " removed from cache")
            
        

    
