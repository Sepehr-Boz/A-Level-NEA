function SelectFile(files, message) {
	let text;
	//format the list files into a 2d string
	let formatted_files = "";
	for (let i=0; i<files.length; i++) {
		formatted_files = formatted_files + "\n" + files[i]
	}
	let selected_file = prompt((formatted_files + "\nEnter a file name"), message)
	//check if cancel has been pressed
	txt = selected_file
	return txt;
};

function InFiles(txt, files) {
	//check if inputted txt is in the list of file names
	let confirmed = false
	for (let i=0; i<files.length; i++) {
		let file_name = files[i]

		if (txt == file_name) {
			confirmed = true
		}
	}
	return confirmed
};

function FindFileID(txt, file_names, file_ids) {
    let id;
	for (let i=0; i<file_names.length; i++) {
		let name = file_names[i]

		if (txt == name) {
			id = file_ids[i];
		}
	}
	return id
}