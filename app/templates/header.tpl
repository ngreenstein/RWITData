<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>{{title}}</title>
	
	<link rel="stylesheet" href="/static/bootstrap-3.3.7/css/bootstrap.css">
	<link rel="stylesheet" href="/static/custom.css">
	
</head>
<body>
	
	<nav class="navbar navbar-default">
		<div class="container">
		
			<a class="navbar-brand" href="/">RWITData</a>
			  
			<ul class="nav navbar-nav">
				<li class="dropdown">
					<a data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Data <span class="caret"></span></a>
					<ul class="dropdown-menu">
						<li><a href="/data/sessions/">Sessions</a></li>
						<li><a href="/data/eno/">E&O</a></li>
					</ul>
				</li>
			
				<li class="dropdown">
					<a data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Admin <span class="caret"></span></a>
					<ul class="dropdown-menu">
						<li><a href="/admin/sessions/">Sessions</a></li>
						<li><a href="/admin/eno/">E&O</a></li>
					</ul>
				</li>
				
			</ul>
			
			<ul class="nav navbar-nav navbar-right">
				<li><a class="" href="/about/">About</a></li>
			</ul>
			
		</div>
	</nav>
	
	<div class="container">
		
		<%
		setdefault("alerts", [])
		if len(alerts) > 0 or (defined("errors") and len(errors) > 0):
			if defined("errors") and len(errors) > 0:
				errTuples = []
				for err in errors:
					if not err:
						break
					end
					errHtml = err[0]
					if len(err) > 1:
						errHtml += "\n<p>Additional information:</p>\n<code>{}</code>".format(err[1])
					end
					errTuples.append((errHtml, "danger"))
				end
				# These two lines effectively add the errors to the beginning of the list of alerts
				errTuples.extend(alerts)
				alerts = errTuples
			end
		
			for alert in alerts:
				if not isinstance(alert, tuple): # Not a tuple, just a string
					alert = (alert, "info")
				elif len(alert) < 2: # A tuple with no type specified
					alert = (alert[0], "info")
				end
				%>
		
		<div class="alert alert-{{alert[1]}} alert-dismissible" role="alert">
			<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
			{{!alert[0]}}
		</div>
		
		% 	end
		% end
