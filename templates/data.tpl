<%
	# The server only allows these two values for dataset; anything else 404s
	datasetNames = {"sessions": "Sessions", "eno": "Education & Outreach"}
	datasetName = datasetNames[dataset]
	pageTitle = datasetName + " Data"
	include("templates/header.tpl", title=pageTitle)
%>

<h1>{{datasetName}} Data</h1>

<h2>Saved Queries</h2>

<div class="panel-group row" id="accordion" role="tablist" aria-multiselectable="true">
	
	<div class="panel panel-default">
		<div class="panel-heading" role="tab" id="sq0-heading">
			<h4 class="panel-title">
				<a role="button" data-toggle="collapse" data-parent="#accordion" href="#sq0-collapse" aria-expanded="true" aria-controls="sq0-collapse">
				Sessions by Tutor
				</a>
			</h4>
		</div>
		<div id="sq0-collapse" class="panel-collapse collapse" role="tabpanel" aria-labelledby="sq0-heading">
			<div class="panel-body">
				<p>Finds all sessions associated with a given tutor, as identified by name and, optionally, class year.</p>
			 	<div class="col-md-4 col-lg-4 no-gutter">
					<form data-toggle="validator" action="/data/sessions/query" method="post">
						<div class="form-group">
							<label for="sq0-param0">Tutor Name</label>
							<input type="text" required="required" class="form-control" id="sq0-param0" name="sq0-param0">
						</div>
						<div class="form-group">
							<label for="sq0-param1">Tutor Year</label>
							<input type="text" class="form-control" id="sq0-param1">
						</div>
						<button type="submit" class="btn btn-primary">Run Query</button>
					</form>
		 		</div>
			</div>
		</div>
	</div>
	
	<div class="panel panel-default">
		<div class="panel-heading" role="tab" id="sq1-heading">
			<h4 class="panel-title">
				<a role="button" data-toggle="collapse" data-parent="#accordion" href="#sq1-collapse" aria-expanded="true" aria-controls="sq1-collapse">
				All Missed Sessions
				</a>
			</h4>
		</div>
		<div id="sq1-collapse" class="panel-collapse collapse" role="tabpanel" aria-labelledby="sq1-heading">
			<div class="panel-body">
				<p>Finds missed sessions in the database.</p>
			 	<div class="col-md-4 col-lg-4 no-gutter">
					<form data-toggle="validator">
						<button type="submit" class="btn btn-primary">Run Query</button>
					</form>
		 		</div>
			</div>
		</div>
	</div>
	
	<div class="panel panel-default">
		<div class="panel-heading" role="tab" id="sq2-heading">
			<h4 class="panel-title">
				<a role="button" data-toggle="collapse" data-parent="#accordion" href="#sq2-collapse" aria-expanded="true" aria-controls="sq2-collapse">
				Presentations By Time
				</a>
			</h4>
		</div>
		<div id="sq2-collapse" class="panel-collapse collapse" role="tabpanel" aria-labelledby="sq2-heading">
			<div class="panel-body">
				<p>Finds presentations that occured at a particular class hour, optionally filtering by x-hours.</p>
			 	<div class="col-md-4 col-lg-4 no-gutter">
					<form data-toggle="validator">
						<div class="form-group">
							<label for="sq2-param0">Class Hour</label>
							<select multiple class="form-control" id="sq2-param0" required="required">
								<option>9L</option>
								<option>10</option>
								<option>11</option>
								<option>12</option>
								<option>2</option>
								<option>10A</option>
								<option>2A</option>
								<option>3A</option>
							</select>
							<p class="multi-select-tip"><em>Hold <kbd>command</kbd> (Mac) or <kbd>control</kbd> (PC) to select multiple options.</em><p>
						</div>
						<div class="form-group">
							<label for="sq2-param1">X-Hour</label>
							<select class="form-control" id="sq2-param1">
								<option></option>
								<option>Yes</option>
								<option>No</option>
							</select>
						</div>
						<button type="submit" class="btn btn-primary">Run Query</button>
					</form>
		 		</div>
			</div>
		</div>
	</div>
	
</div>


<h2>Custom Query</h2>
<p>coming soon</p>

% include("templates/footer.tpl")
