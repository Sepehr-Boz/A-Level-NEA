from flask import Flask, render_template, request, url_for, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import *
from decode import *
import socket as s

site = Flask(__name__)
socket = SocketIO(site, cors_allowed_origins="*")


#CUSTOM FUNCTIONS#

#start the database
def InitDB():
    #start the db 
    JE = Database("JointEffort.db")
    JE.OpenDB()
    #add tables if db doesnt exist yet
    JE.AddTable("Users (userID integer, email text, name text, password text, loggedIn text)")
    JE.AddTable("Files (fileID integer, numUsers integer, fileName text)")
    JE.AddTable("UserConnections (userID integer, fileID integer)")
    JE.AddTable("FileConnections (fileID integer, contentID integer)")
    JE.AddTable("History (contentID integer, userID integer, content text, time text)")
    #JE.CloseDB()

#get id from url
def GetIDFromURL(url):
    #loop through the last 3 to last 1 character to check for different length ids
    for length in range(-3, 0, 1):
        try:
            id = int(url[length::])
        except ValueError:
            pass
    return id

#get the history of a file
def GetFileHistory(file_id):
    file_name = Files.GetFileName(file_id)
    #get the history disctionary and reassign the editor id to the user name
    file_history = Historys.GetHistory(file_id)
    for date in file_history:
        values = file_history[date]
        user_id = values[1]
        username = Users.GetUserName(user_id)
        file_history[date][1] = username
    file = {file_name: file_history}

    return file
    #example = {"Joint Effort": {"12/05/2022": ['abcd', 'sep']}}
    #structure = {"file_name": {"datetime_edited": ["changed_content", "editor_name"], "datetime_edited": [...]}}...

def GetHostIP():
    host_ip = s.gethostbyname(s.gethostname())
    #host_ip += ":5000"
    return host_ip

#keep track of rooms
class Rooms():
    def __init__(self):
        self.rooms = []

    #add a room whenever someone creates a room
    def AddRoom(self, name):
        self.rooms.append(name)

    #remove a user's room whenever they leave
    def RemoveRoom(self, id):
        self.rooms.remove(id)

    #checks if a room exists
    def CheckIfExists(self, name):
        exists = False
        if name in self.rooms:
            exists = True
        
        return exists

#SOCKET FUNCTIONS#

#joining a room
@socket.on("JOIN")
def Join(data):
    print(data)

    rooms = []

    room_name = data["room"]
    url = data["url_info"]
    user_id = GetIDFromURL(url)

    if room_name == None:
        pass
    else:
        join_room(room_name)
        sessions.AddRoom(room_name)
        rooms.append(room_name)

    join_room(user_id)
    sessions.AddRoom(user_id)
    rooms.append(user_id)

    print("Someone new has joined rooms:", rooms)

#leaving a room
@socket.on("LEAVE")
def Leave(data):
    print(data)

    rooms = []

    room_name = data["room"]
    url = data["url_info"]
    user_id = GetIDFromURL(url)

    if room_name == None:
        pass
    else:
        leave_room(room_name)
        sessions.RemoveRoom(room_name)
        rooms.append(room_name)
    
    leave_room(user_id)
    sessions.RemoveRoom(user_id)
    rooms.append(user_id)

    print("Someone has left room", rooms)

#communicating with client
@socket.on("MESSAGE")
def HandleMessage(data):
    #extract data from dictionary
    room = data["room"]
    box = data["box"]
    data = data["data"]

    print("Message:", data, "Room:", room)
    #emit to the room, and box, and append data
    emit(box, data, room=room)

@socket.on("RENAME")
def Rename(data):
    #extract the data from dictionary
    file_id = data["file_id"]
    new_name = data["new_name"]

    #change the record in Files with the new name
    Files.UpdateRecord(file_id, "fileName", new_name)

@socket.on("COPY")
def Copy(data):
    file_id = data["file_id"]
    user_id = data["user_id"]

    #get file details
    Files.GetCurrentID()
    current_id = Files.current_id + 1
    file_name = Files.SearchRecord("fileID", file_id)[0][2]
    #add a new record to files with the same details but num of users set to 1
    Files.AddRecord(f"{current_id}, 1, '{file_name}'")
    #add connection between user and new file
    UserConnections.AddConnection(user_id, current_id)
    #get the content ids of the old file
    content_ids = FileConnections.GetContentIDs(file_id)
    #add to file connections connections between new file id and the content ids
    for id in content_ids:
        FileConnections.AddConnection(current_id, id)


@socket.on("DELETE")
def Delete(data):
    user_id = int(data["user_id"])
    file_id = int(data["file_id"])

    UserConnections.DelConnection(user_id, file_id)

#saving a current file
@socket.on("SAVE")
def SaveFile(data):
    #extract data from dictionary
    url = data["url_info"] #structure is http://hostipaddress/collab_doc/room/id
    user_id = GetIDFromURL(url)

    room = data["room"]
    name = data["name"]
    content = data["code"]
    try:
        #if file id was passed then update the record in files
        file_id = data["file_id"]
        Files.ExistentFile(file_id, user_id, name, content)
    except KeyError:
        #if file id doesnt exist create a new record in files
        Files.NewFile(user_id, name, content)
    #emit a confirmation to the user
    emit("POPUP_SAVE", room=user_id)

#opening a file
@socket.on("OPEN")
def OpenFile(data):
    #extract data from dictionary
    room = data["room"]
    url = data["url_info"]

    user_id = GetIDFromURL(url)
    #get all file ids that are linked to user id
    list_of_files = UserConnections.GetFileIDs(user_id)
    file_names = []
    #append all file names
    for file_id in list_of_files:
        file_names.append(Files.GetFileName(file_id))

    #emit to room the list of files to open
    emit("POPUP_OPEN", {"files": file_names, "file_ids": list_of_files}, room=user_id)


#opening a file continued...
@socket.on("OPEN_FILE")
def OpenFile(data):
    #extract data from dictionary
    file_name = data["name"]
    file_id = data["file_id"]
    room = data["room"]
    #find file content from id
    content = Files.GetCurrentContent(file_id)
    #emit to room, to CODE with the content to update
    emit("CODE", content, room=room)
    emit("TITLE", file_name, room=room)


##take out if doesnt work by 17th
#running current document
@socket.on("RUN")
def RunFile(data):
    #extract data from dictionary
    code = data["code"]
    room = data["room"]
    #save code data as python file
    Code = Decode(code)
    #Code.GetLines()
    result = Code.GetOutput()
    #execute python file and get output
    #emit to room, to console, with output
    print("RUN FUNCTION CALLED")
    emit("CONSOLE", result, room=room)


#FLASK ROUTES#

#the homepage
@site.route("/")
def HomePage():
    return render_template("homepage.html")

#the login page
@site.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "GET":
        #load the page
        return render_template("login.html")
    elif request.method == "POST":
        #extract data from the form
        username = request.form["name"]
        password = request.form["pass"]
        #check if details match record in Users
        confirmed = Users.CheckDetails(username, password)
        if confirmed == True:
            #get the userID
            user_id = Users.GetUserID(username, password)
            #load profile page if passed
            Users.logUser(user_id)
            return redirect(f"/profile/{user_id}")
        else:
            #reload login page if not passed
            return render_template("login.html", method="GET", error_message="Your username or password is incorrect.")

#the register page
@site.route("/register", methods=["GET","POST"])
def Register():
    if request.method == "GET":
        #load register page
        return render_template("register.html")
    elif request.method == "POST":
        #extract details from the form
        email = request.form["email"]
        username = request.form["name"]
        password = request.form["pass"]
        password_check = request.form["pass_check"]

        #check if password meets the requirements
        special_characters = ['~', ':', "'", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`', '}', '.', '_', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/']
        numbers = "1234567890"

        pass1 = False
        pass2 = False
        pass3 = False
        if len(password) >= 8:
            pass1 = True
        for number in numbers:
            if number in password:
                pass2 = True
        for character in special_characters:
            if character in password:
                pass3 = True

        if pass1 == True and pass2 == True and pass3 == True:
            pass
        else:
            return render_template("register.html", error_message="The password did not meet standards")
                    

        #check if password and re-entered password are equal
        if password == password_check:
            pass
        else:
            return render_template("register.html", error_message="The passwords did not match")

        #add the details to the Users table + check if details are already in table
        confirmed = Users.AddDetails(email, username, password)
        if confirmed == True:
            #new user so pass to profile
            user_id = Users.GetUserID(email, password)
            Users.logUser(user_id)
            return redirect(url_for("Profile", id=user_id))
        else:
            #current user so reload register page
            return render_template("register.html", error_message="The user already has an account")
        
#profile page + id variable passed through url
@site.route("/profile/<id>", methods=["GET","POST"])
def Profile(id):
    #get details based on userID
    user_record = Users.SearchRecord("userID", id)[0]
    email = user_record[1]
    name = user_record[2]
    user_id = id

    if request.method == "GET":
        #get the users file histories
        files = {}
        file_ids = UserConnections.GetFileIDs(id)
        for id in file_ids:
            files[id] = Files.GetFileName(id)

        local_host = GetHostIP() + ":5000"
        
        #load profile with details5
        return render_template("profile.html", email=email, user=name, id=user_id, files=files, local_host_ip=local_host)
    elif request.method == "POST":
        #when button pressed
        #get room name
        #only allow a room to be created if it doesnt already exist +
        #only allow a room to be joined if it exists
        try:
            room_name = request.form["create_session"]
            if sessions.CheckIfExists(room_name) == True:
                #if room exists refresh page
                return redirect(url_for("Profile", id=user_id))
            else:
                #if room doesnt exist add rooms and join
                pass
        except KeyError:
            room_name = request.form["join_session"]
            if sessions.CheckIfExists(room_name) == True:
                #if room exists join
                pass
            else:
                #if room doesnt exist
                return redirect(url_for("Profile", id=user_id))
                
        return redirect(f"/collab_doc/{room_name}/{user_id}")


@site.route("/history/<user_id>/<file_id>", methods=["GET","POST"])
def History(user_id, file_id):
    if request.method == "GET":
        history = GetFileHistory(file_id)
        return render_template("history.html", files=history)
    elif request.method == "POST":
        #redirect to profile page
        return redirect(f"/profile/{user_id}")

#collab_doc page + room_name + clientid variables passed through url
@site.route("/collab_doc/<room_name>/<user_id>", methods=["GET", "POST"])
def CollabDoc(room_name, user_id):
    if request.method == "GET":

        local_host = GetHostIP() + ":5000"

        #load collab_doc
        return render_template("collab_doc.html", room=room_name, local_host_ip=local_host)
        #create function to find local host ip and pass it to the local_host_ip variable

    elif request.method == "POST":
        return redirect(f"/profile/{user_id}")

#MAINLOOP#

if __name__ == "__main__":
    #add object to keep track of rooms
    sessions = Rooms()
    #start the database
    InitDB()
    #add variables to indicate each table
    #Users table
    Users = UserTable("JointEffort.db", "Users", "userID, email, name, password, loggedIn")
    #Files table
    Files = FileTable("JointEffort.db", "Files", "fileID, numUsers, fileName")
    #Connections table ~ userID and fileID
    UserConnections = UserConnectionTable("JointEffort.db", "UserConnections", "userID, fileID")
    #Connections table ~ fileID and contentID
    FileConnections = FileConnectionTable("JointEffort.db", "FileConnections", "fileID, contentID")
    #History table
    Historys = HistoryTable("JointEffort.db", "History", "contentID, userID, content, time")


    tables = [Users, Files, UserConnections, FileConnections, Historys]
    Files.AddTables(tables)
    Historys.AddTables(tables)

    Users.SetLoggedIn()

    host_ip = GetHostIP()

    socket.run(site, debug=True, host=host_ip)
