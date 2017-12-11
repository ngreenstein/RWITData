<%
pageTitle = datasetName + " Admin"
include(basePath + "app/templates/header.tpl", title = pageTitle, alerts = get("alerts", None))
%>

<h1>{{datasetName}} Admin</h1>

<h2>Export from Database</h2>

<div class="row container">
	<p class="col-md-8 col-lg-8 no-gutter">Exports the RWITData {{datasetName.lower()}} database, either for all time or for specific terms. The SQLite option produces a single file containing a relational database, which is easily queried through database software and statistics packages like R, and can be imported later using this page. The CSVs option produces a zip file containing a series of CSV files, which are readable by text editors and spreadsheet software, <span class="text-danger">but cannot be imported by RWITData</span>. SQLite provides a richer representation of the data, and is recommended whenever possible. SQLite exports are also an effective way to create backups and exchange data between RWITData users.</p>
</div>

<div class="row container">
	<form class="col-md-4 col-lg-4 no-gutter" data-toggle="validator" action="/admin/{{dataset}}/export/" method="post">
		<div class="form-group">
			<label for="exportTerms">Terms:</label>
			<input type="text" class="form-control" id="exportTerms" name="exportTerms" placeholder="e.g. '17S, 17X'" pattern="(\d{2}(F|W|S|X)(,\s+)?)+">
			<p class="form-tip"><em>Leave blank for all terms. Separate multiple terms with commas.</em><p>
		</div>
		<input type="submit" class="btn btn-primary" name="sqlite" value="Export SQLite">
		<input type="submit" class="btn btn-default" name="csv" value="Export CSVs">
	</form>
</div>

<h2>Import to Database</h2>

<div class="row container">
	<p class="col-md-8 col-lg-8 no-gutter">Imports data into the RWITData {{datasetName.lower()}} database from a SQLite file created by RWITData's export function, or a CSV file created by RWIT Online's export function. Note that CSV files created by RWITData's export function are not supported. Adding to the existing database will combine new data with old (ignoring duplicates), and replacing the existing database will destroy all old data and import new. <span class="text-danger">Replacing the existing database will destroy data and cannot be undone.</span></p>
</div>

<div class="row container" id="importRow">
	<form class="col-md-4 col-lg-4 no-gutter" id="importForm" data-toggle="validator" action="/admin/{{dataset}}/import/" method="post" enctype="multipart/form-data">
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

% include(basePath + "app/templates/footer.tpl", scripts=["/static/admin.js"])
