% include(basePath + "app/templates/header.tpl", title="Saved Query Results")

<h1>{{query.name}}</h1>

<table class="table table-striped table-hover table-condensed table-bordered">
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

<p>{{len(results)}} rows returned</p>

% include(basePath + "app/templates/footer.tpl")
