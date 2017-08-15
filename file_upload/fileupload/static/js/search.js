function filter_files(string) {
	var x = 0;
	while (true) {
		var tr_str = "file_" + x;
		var element = document.getElementById(tr_str);
		if (element == null) {
			return;
		}
		if (element.getAttribute("name").search(string) != -1) {
			$(element).show();
		}
		else {
			$(element).hide();
		}
		x += 1;
	}
}