<%
pageTitle = datasetName + " Admin"
include("templates/header.tpl", title=pageTitle)
%>

<h1>{{datasetName}} Admin</h1>

<h2>Export from Database</h2>

<div class="row container">
	<p class="col-md-8 col-lg-8 no-gutter">Exports the RWITData {{datasetName.lower()}} database, either for all time or for specific terms. The SQLite option produces a single file containing a relational database, which is easily queried through database software and statistics packages like R, and can be imported later using this page. The CSVs option produces a zip file containing a series of CSV files, which are readable by text editors and spreadsheet software, <span class="text-danger">but cannot be imported by RWITData</span>. SQLite provides a richer representation of the data, and is recommended whenever possible. SQLite exports are also an effective way to create backups and exchange data between RWITData users.</p>
</div>

<div class="row container">
	<form class="col-md-4 col-lg-4 no-gutter" data-toggle="validator" action="/admin/{{dataset}}/export" method="post">
		<div class="form-group">
			<label for="exportTerms">Terms:</label>
			<input type="text" class="form-control" id="exportTerms" name="exportTerms" placeholder="e.g. '17S, 17X'" pattern="(?i)(\d{2}(F|W|S|X)(,\s+)?)+">
			<p class="form-tip"><em>Leave blank for all terms. Separate multiple terms with commas.</em><p>
		</div>
		<input type="submit" class="btn btn-primary" name="sqlite" value="Export SQLite">
		<input type="submit" class="btn btn-default" name="csv" value="Export CSVs">
	</form>
</div>

<h2>Import to Database</h2>

<div class="row container">
	<p class="col-md-8 col-lg-8 no-gutter">Description</p>
</div>

<div class="row container" id="importRow">
	<form class="col-md-4 col-lg-4 no-gutter" id="importForm" data-toggle="validator" action="/admin/{{dataset}}/import" method="post" enctype="multipart/form-data">
		<div class="form-group">
			<label for="importFile">File</label>
			<input type="file" id="importFile" name="importFile" required accept=".csv,.db,.sqlite,.sqlite3,.db3">
			<p class="form-tip"><em>SQLite and CSV files accepted.</em><p>
		</div>
		<input type="submit" class="btn btn-primary" name="addToExisting" value="Add to Existing">
		<input type="submit" class="btn btn-danger" id="replaceExistingButton" name="replaceExisting" value="Replace Existing">
	</form>
</div>

<div id="replaceAlert" class="row container hidden">
	<div class="alert alert-danger col-md-8 col-lg-8 top-margin" role="alert">
		<p>
			<strong>Replacing the database cannot be undone.</strong><br>
			All existing data will be deleted permanently, and new data from the file you selected will be imported. Only do this if you are sure that you no longer need anything from the existing database. Consider using the Export SQLite function above to back up the existing database before continuing.
		</p>
		<button id="continueButton" class="btn btn-danger top-margin" name="replaceExisting">Continue</button>
	</div>
</div>

% include("templates/footer.tpl", scripts=["/static/admin.js"])
