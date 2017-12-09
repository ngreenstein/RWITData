$(document).ready(function()
{
	$("#back-button").click(function(event) {
		window.history.back();
		event.preventDefault();
	});
});