$(document).ready(function()
{
	var options = {
		widthFixed: true,
		theme : "bootstrap",
		headerTemplate : '{content} {icon}',
		widgets: ["uitheme", "zebra", "stickyHeaders", "filter"],
		widgetOptions : {
			zebra : ["even", "odd"],
			filter_cssFilter: "form-control",
		}
	};
	$("#results-table").tablesorter(options);
});
