function bodyonload(){
	$('admin_left').style.height = Math.max(window.screen.availHeight-110, document.body.scrollHeight-50) + 'px';
}