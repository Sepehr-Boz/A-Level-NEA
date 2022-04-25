function CreateDeleteButton(section, file_id) {
    let button = document.createElement("button");
    let name = document.createTextNode("DELETE");
    button.appendChild(name);
    button.value = "DELETE";
    button.id = file_id;

    section.appendChild(button);
}

function CreateCopyButton(section, file_id) {
    let button = document.createElement("button");
    let name = document.createTextNode("COPY");
    button.appendChild(name);
    button.value = "COPY";
    button.id = file_id;

    section.appendChild(button);
}

function CreateRenameButton(section, file_id) {
    let button = document.createElement("button");
    let name = document.createTextNode("RENAME");
    button.appendChild(name);
    button.value = "RENAME";
    button.id = file_id;

    section.appendChild(button);
}

function CreateBreak(section) {
    let br = document.createElement("br");

    section.appendChild(br);
}

function NewLink(section, file_id, file_name, user_id) {
    let anchor = document.createElement("a");
    let link = document.createTextNode(file_name);
    anchor.appendChild(link);
    anchor.title = file_name;
    anchor.href = "/history/"+user_id.toString()+"/"+file_id.toString();

    section.appendChild(anchor);
};

function CreateBar(file_id, file_name, user_id) {
    //create an area for each file and options between Files:
    let bar = document.createElement("div")
    bar.className = "bar"
    document.body.appendChild(bar)
    CreateBreak(bar)
    NewLink(bar, file_id, file_name, user_id)
    CreateRenameButton(bar, file_id)
    CreateCopyButton(bar, file_id)
    CreateDeleteButton(bar, file_id)
}

function GetUserID(url) {
    let found = false;
    let index = 0;
    while (found == false) {
        index --;
        let user_id = url.slice(index)
        //find the index where the last / occurs and increment the index to find where the user id starts
        if (user_id.includes("/") == true) {
            index ++;
            found = true;
        }
    }

    let user_id = url.slice(index);
    return user_id;
}

function NewFileName() {
    let new_name = prompt("Please enter the new file name")
    while (new_name == "" || new_name == null) {
        new_name = prompt("Please enter a valid file name");
    }

    return new_name;
}