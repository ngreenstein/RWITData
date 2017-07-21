<%
	# The server only allows these two values for dataset; anything else 404s
	datasetNames = {"sessions": "Sessions", "eno": "Education & Outreach"}
	datasetName = datasetNames[dataset]
	pageTitle = datasetName + " Data"
	include("templates/header.tpl", title=pageTitle)
%>

<h1>{{datasetName}} Data</h1>

% include("templates/footer.tpl")