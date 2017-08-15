function filter_files(string) {
	var x = 0;
	var table = document.getElementById("file_table");
	var files = table.childNodes;
	var file_count = files.length;
	for (var i = 0; i < file_count; i++) {
		element = files[i];
		name = element.getAttribute("name");
		if (name.substring(name.lastIndexOf('/'), name.lastIndexOf('_do_')).search(string) != -1) {
			$(element).show();
		}
		else {
			$(element).hide();
		}
	}
}