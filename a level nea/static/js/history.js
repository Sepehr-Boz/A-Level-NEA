function UpdateText(file) {
    //extract the data
    let file_name = file[0]
    let file_content = file[1]
    let file_time = file[2][0]
    let editor_name = file[2][1]

    //update the values at each of the variable positions
    document.getElementById("file_name").innerHTML = file_name;
    document.getElementById("content").value = file_content;
    document.getElementById("time_edited").innerHTML = file_time;
    document.getElementById("editor_name").innerHTML = editor_name;
}

function ReFormatContent(content) {
    //replace all the changes to content after parsing the data
    content = content.replace(/\n/g, "\n")
    content = content.replace(/@QUOTE/g, '"')

    return content
}