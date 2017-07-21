<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>{{title}}</title>
	
	<link rel="stylesheet" href="/static/bootstrap-3.3.7/css/bootstrap.css">
	<link rel="stylesheet" href="/static/bootstrap-3.3.7/css/bootstrap-theme.css">
	
</head>
<body>
	
	<nav class="navbar navbar-default">
		<div class="container">
		
			<a class="navbar-brand" href="/">RWITData</a>
			  
			<ul class="nav navbar-nav">
				<li class="dropdown">
					<a data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Data <span class="caret"></span></a>
					<ul class="dropdown-menu">
						<li><a href="/data/sessions">Sessions</a></li>
						<li><a href="/data/eno">E&O</a></li>
					</ul>
				</li>
			
				<li class="dropdown">
					<a data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Admin <span class="caret"></span></a>
					<ul class="dropdown-menu">
						<li><a href="/admin/sessions">Sessions</a></li>
						<li><a href="/admin/eno">E&O</a></li>
					</ul>
				</li>
				
			</ul>
			
			<ul class="nav navbar-nav navbar-right">
				<li><a class="" href="/about">About</a></li>
			</ul>
			
		</div>
	</nav>
	
	<div class="container">
