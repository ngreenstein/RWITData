% include(basePath + "app/templates/header.tpl", title="Query Results")

<link rel="stylesheet" href="/static/theme.bootstrap_3.css">

<h1>{{queryTitle}}</h1>

<p>{{len(results)}} rows returned</p>

<div class="form-group">
	<a class="btn btn-default" href="../export-results/{{resultsHash}}/">Export CSV</a>
</div>

<table class="table table-hover table-condensed table-bordered" id="results-table">
	<thead>
		<tr>
			% for col in rowHeads:
			<th>{{col}}</th>
			% end
		</tr>
	</thead>
	<tbody>
		% for row in results:
		<tr>
			% for col in row:
			<td>{{col}}</td>
			% end
		</tr>
		% end
	</tbody>
</table>

% include(basePath + "app/templates/footer.tpl", scripts = ["/static/jquery.tablesorter.combined.js", "/static/results.js"])
