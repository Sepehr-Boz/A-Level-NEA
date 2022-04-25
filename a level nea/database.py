import sqlite3 as sql
from datetime import datetime

#Classes in capital first
#methods in ParselCase
#variables in lower_snake_case

class Database():
    def __init__(self, db_name):
        #db_name is name of database assigned in program
        self.db_name = db_name
    
    #opens database
    def OpenDB(self):
        #creates a connection with the database and opens it
        self.connection = sql.connect(self.db_name, check_same_thread=False)
        #creates a tool to edit the database with
        self.cursor = self.connection.cursor()

    #closes database
    def CloseDB(self):
        self.connection.close()

    #saves changes to database
    def Save(self):
        self.connection.commit()
            
    #adds a table to the database
    def AddTable(self, table):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table};""")
        self.Save()

#child class for table-specific functions
class Table(Database):
    def __init__(self, db_name, table_name, columns):
        #inherit Database attributes
        super().__init__(db_name)
        #assign Table attributes
        self.table_name = table_name
        self.columns = f"({columns})"
        #incrementing id
        self.current_id = 0

        Database.OpenDB(self) #to create a connection and cursor

    #for adding connections to other tables
    def AddTables(self, tables):
        #pass in list tables
        self.tables = {"users": tables[0], "files": tables[1], "user_connections": tables[2], "file_connections": tables[3], "history": tables[4]}
        return self.tables

    #testing
    def PrintAllDetails(self):
        print(self.table_name)
        print(self.columns)
        print(self.current_id)

    #add a record to the table
    def AddRecord(self, values):
        self.cursor.execute(f"""INSERT INTO {self.table_name}{self.columns} VALUES ({values});""")
        self.Save()

    #delete a record from the table
    def DelRecord(self, column, record):
        self.cursor.execute(f"DELETE from {self.table_name} WHERE {column} = {record};")
        self.Save()

    #search whole table
    def SearchTable(self):
        values = []
        for record in self.cursor.execute(f"SELECT * FROM {self.table_name};"):
            values.append(record)
        return values

    #search all values within a column
    def SearchColumn(self, column_name):
        values = []
        for record in self.cursor.execute(f"SELECT {column_name} FROM {self.table_name};"):
            values.append(record)
        return values

    #update all the values in a column
    def UpdateColumn(self, column_name, new_value):
        self.cursor.execute(f"""UPDATE {self.table_name} SET {column_name} = '{new_value}';""")
        self.Save()

    #find record that meets a condition
    def SearchRecord(self, column_name, value):
        values = []
        for record in self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE {column_name} = '{value}';"):
            values.append(record)
        return values

    #update a record in table
    def UpdateRecord(self, id, column_name, value):
        #check if its the files or users table
        if "fileID" in self.columns:
            unique_id = "fileID"
        else:
            unique_id = "userID"
        self.cursor.execute(f"UPDATE {self.table_name} SET {column_name} = '{value}' WHERE {unique_id} = {id};")
        self.Save()

    #find most recent id in table
    def GetCurrentID(self):
        table_values = self.SearchTable() #will return a "2d" array with records inside a list
        try:
            last_record = table_values[-1] #will return the last record which will have the current id
            current_id = last_record[0]
        except IndexError: #will occur if the table is empty so far
            current_id = 0
        self.current_id = current_id




#users table
class UserTable(Table):
    def __init__(self, db_name, table_name, columns):
        #inherit Table attributes
        super().__init__(db_name, table_name, columns)

    #for determining whether to search through the "email" or "name" column
    def DetermineColumn(self, username):
        mail_names = ["@gmail", "@yahoo", "@hotmail"]
        column = "name" #set default column to name

        #loop through mail names to check if they're present in username
        for mail in mail_names:
            if mail in username:
                #set column to "email" if a mail name is present in username
                column = "email"
            else:
                pass

        return column

    #for checking user details
    def CheckDetails(self, username, password):
        confirmed = False

        column = self.DetermineColumn(username)

        #returns a 2d array of records that match name/email
        possible_users = list(self.SearchRecord(column, username))
        for user in possible_users:
            #check password
            if user[3] == password:
                #check if logged in or not
                if user[4] == "false":
                    confirmed = True
                else:
                    pass
            else:
                pass

        return confirmed

    #for adding record to user table
    def AddDetails(self, email, username, password):
        #increment userID for each new user
        self.GetCurrentID()
        self.current_id += 1

        #check if user already exists in user table
        exists = False
        all_emails = self.SearchColumn("email")
        for mail in all_emails:
            if email in mail:
                exists = True
            else:
                pass
        
        #only add a new record to user table if user does not already have an account
        if exists == False:
            confirmed = True
            values = f"{self.current_id}, '{email}', '{username}', '{password}', 'false'"
            self.AddRecord(values)
        else:
            confirmed = False

        #confirmed is a flag checking whether or not the details have been added
        return confirmed

    #get userID
    def GetUserID(self, username, password):
        #find out which column to search through
        #+ finds out whether username is a name or email
        column = self.DetermineColumn(username)

        #check for records in user table
        #find out records that match name and password
        name_matches = self.SearchRecord(column, username)
        pass_matches = self.SearchRecord("password", password)
        #find the intersection between name_matches and pass_matches
        final_match = set(name_matches).intersection(pass_matches)
        final_match = list(final_match)[0]
        user_ID = final_match[0]

        return user_ID

    #get and return name from user id
    def GetUserName(self, user_id):
        record = self.SearchRecord("userID", user_id)[0]
        return record[2]

    def GetUserEmail(self, user_id):
        record = self.SearchRecord("userID", user_id)[0]
        return record[1]

    #set all loggedIn values to false at the start of the program
    def SetLoggedIn(self):
        self.UpdateColumn("loggedIn", "false")

    #change a loggedIn status between true and false
    def logUser(self, user_id):
        #get user record
        user_record = self.SearchRecord("userID", user_id)[0]
        #check if loggedIn is true or false
        if user_record[4] == "true":
            log = "false"
        elif user_record[4] == "false":
            log = "true"
        else:
            print("An error has occurred")
        #switch loggedIn to the opposite
        self.UpdateRecord(user_id, "loggedIn", log)


class FileTable(Table):
    def __init__(self, db_name, table_name, columns):
        super().__init__(db_name, table_name, columns)

    def AddTables(self, tables):
        super().AddTables(tables)
        del self.tables["files"]

    #updating file history
    def UpdateFile(self, file_id, user_id, content):
        content_id = self.tables["history"].NewEdit(user_id, content)
        self.tables["file_connections"].AddRecord(f"{file_id}, {content_id}")
        #call file_connectiosn from self.tables and add record to the table
        #call history from self.tables and add record to history

    #updates an existent file
    def ExistentFile(self, file_id, user_id, file_name, content):
        print("existent file run")
        #get the record from Files that match file_id
        record = self.SearchRecord("fileID", file_id)[0]
        #update the record if the name is different
        if record[2] != file_name:
            self.UpdateRecord(file_id, "fileName", file_name)
        else:
            pass
        self.UpdateFile(file_id, user_id, content)
        #get the list of user ids that are connected to the file id in UserConnections table
        user_ids = self.tables["user_connections"].GetUserIDs(file_id)
        num_of_users = len(user_ids)
        #if the user id is not in the list then increment the number in numOfUsers in Files
        if user_id not in user_ids:
            num_of_users += 1
            self.UpdateRecord(file_id, "numOfUsers", num_of_users)
            self.tables["user_connections"].AddRecord(f"{user_id}, {file_id}")
        else:
            pass
        
    #adding a new file
    def NewFile(self, user_id, file_name, content):
        print("new file run")
        self.GetCurrentID()
        self.current_id += 1
        num_of_users = 1
        #add new record to Files with increment file_id and file_name and numofusers set to 1
        self.AddRecord(f"{self.current_id}, {num_of_users}, '{file_name}'")
        #add new connection in userconnections (between user_id and new file_id) and fileconnections (between new file_id and new content_id)
        self.tables["user_connections"].AddRecord(f"{user_id}, {self.current_id}")
        #add new history record with content id
        self.UpdateFile(self.current_id, user_id, content)

    #for getting the name of a file by its id
    def GetFile(self, file_id):
        record = self.SearchRecord("fileID", file_id)[0]
        return record

    #getting the file name
    def GetFileName(self, file_id):
        record = self.GetFile(file_id)
        file_name = record[2]

        return file_name

    #getting the file content
    def GetCurrentContent(self, file_id):
        #get content ids
        content_ids = self.tables["file_connections"].GetContentIDs(file_id)
        #get the last record to find latest content id
        content_id = content_ids[-1]
        #get the record in history through content id
        record = self.tables["history"].SearchRecord("contentID", content_id)[0]
        #get content and return it
        content = record[2]
        return content

#connection tables will only have 2 columns - both ids
class ConnectionTable(Table):
    def __init__(self, db_name, table_name, columns):
        super().__init__(db_name, table_name, columns)

    #for adding a record
    def AddConnection(self, column_a, column_b):
        values = f"{column_a}, {column_b}"
        self.AddRecord(values)

    def GetID(self, column, id):
        id_matches = self.SearchRecord(column, id)
        ids = list(id_matches)

        return ids


class UserConnectionTable(ConnectionTable):
    def __init__(self, db_name, table_name, columns):
        super().__init__(db_name, table_name, columns)
      
    #for getting file ids that are linked to user id
    #all files that a user worked on
    def GetFileIDs(self, user_id):
        ids = []
        records = self.GetID("userID", user_id)
        for record in records:
            ids.append(int(record[1]))

        return ids

    #for getting user ids that are linked to file id
    #all users that worked on a file
    def GetUserIDs(self, file_id):
        ids = []
        records = self.GetID("fileID", file_id)
        for record in records:
            ids.append(int(record[0]))

        return ids

    def DelConnection(self, user_id, file_id):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE userID = {user_id} AND fileID = {file_id};")
        self.Save()
        print("connection deleted")

class FileConnectionTable(ConnectionTable):
    def __init__(self, db_name, table_name, columns):
        super().__init__(db_name, table_name, columns)

    #for getting content ids that are linked to file id
    #history of a files edits
    def GetContentIDs(self, file_id):
        ids = []
        records = self.GetID("fileID", file_id)
        for record in records:
            ids.append(int(record[1]))

        return ids

class HistoryTable(Table):
    def __init__(self, db_name, table_name, columns):
        super().__init__(db_name, table_name, columns)

    def AddTables(self, tables):
        super().AddTables(tables)
        del self.tables["history"]

    def GetTime(self):
        #get time
        time = datetime.now()
        time = str(time)[:-7] #removes the milliseconds from the time
        return time

    def NewEdit(self, user_id, content):
        self.GetCurrentID()
        self.current_id += 1
        current_time = self.GetTime()
        values = f"{self.current_id}, {user_id}, '{content}', '{current_time}'"
        self.AddRecord(values)

        return self.current_id

    def SpliceContent(self, content):
        #replace " in content as it won't be parsed correctly into history
        content = content.replace('"', "@QUOTE")

        return content



    def GetHistory(self, file_id):
        #get content ids from file id (file connections)
        content_ids = self.tables["file_connections"].GetContentIDs(file_id)
        history = {}
        for id in content_ids:
            #get contents from every content id
            record = self.SearchRecord("contentID", id)[0]
            editor_id = record[1]
            content = self.SpliceContent(record[2].replace("\n", "\\n"))
            #content = record[2].replace("\n", "\\n")
            time_edited = record[3]
            #append every content to a dictionary
            history[time_edited] = [content, editor_id]

        return history