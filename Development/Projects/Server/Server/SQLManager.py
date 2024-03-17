# Contains SQL management functions for build wide transactions

# imports
from asyncio import Server
from asyncio.windows_events import NULL
import pyodbc as DB

SERVER = 'Skylar-Music'
DATABASE = 'Application'
USERNAME = '<admin>'
PASSWORD = '<password>'


class SQLManager():
    
    def __init__(self):
        connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE}' # UID={USERNAME};PWD={PASSWORD}
        self.dbConnection = DB.connect(connectionString)
        
    def select(self, SQL, variables = None):
        #split variables into list
        if variables != None:
            if isinstance(variables, str):
                splitVariables = variables.split(',')
            else:
                splitVariables = str(variables)
                
            # establish cursor
            cursor = self.dbConnection.cursor()
            cursor.execute(SQL, *splitVariables)
        else:
            # establish cursor
            cursor = self.dbConnection.cursor()
            cursor.execute(SQL)
        
        return cursor.fetchall()
        
    def update(self, SQL, variables):
        #split variables into list
        splitVariables = variables.split(',')

        # establish cursor and execute insert query
        cursor = self.dbConnection.cursor()
        cursor.execute(SQL, *splitVariables)
        # commit transaction
        cursor.commit()
        cursor.close()

    # example
    '''
    SQL_STATEMENT = """
    INSERT SalesLT.Product (
    Name, 
    ProductNumber, 
    StandardCost, 
    ListPrice, 
    SellStartDate
    ) OUTPUT INSERTED.ProductID 
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """
    '''
    # insert function, variables should be comma dilimeted list
    def insert(self, SQL, variables):
        
        #split variables into list
        splitVariables = variables.split(',')

        # establish cursor and execute insert query
        cursor = self.dbConnection.cursor()
        cursor.execute(SQL, *splitVariables)
        # commit transaction
        cursor.commit()
        cursor.close()

    def __del__(self):
        self.dbConnection.close()