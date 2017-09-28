<%
pageTitle = datasetName + " Data"
include(basePath + "app/templates/header.tpl", title=pageTitle)
%>

<h1>{{datasetName}} Data</h1>

<h2>Saved Queries</h2>

% if len(savedQueries) > 0:

<div class="panel-group row" id="accordion" role="tablist" aria-multiselectable="true">
	
	<%
	queryIndex = 0
	for savedQuery in savedQueries:
	%>
	
	<div class="panel panel-default">
		<div class="panel-heading" role="tab" id="sq{{queryIndex}}-heading">
			<h4 class="panel-title">
				<a role="button" data-toggle="collapse" data-parent="#accordion" href="#sq{{queryIndex}}-collapse" aria-expanded="true" aria-controls="sq{{queryIndex}}-collapse">
				{{savedQuery.name}}
				</a>
			</h4>
		</div>
		<div id="sq{{queryIndex}}-collapse" class="panel-collapse collapse" role="tabpanel" aria-labelledby="sq{{queryIndex}}-heading">
			<div class="panel-body">
				<p>{{savedQuery.description}}</p>
			 	<div class="col-md-4 col-lg-4 no-gutter">
				 	
					<form data-toggle="validator" action="/data/{{dataset}}/saved-query/" method="post">
						
						<input type="hidden" name="hash" value="{{savedQuery.hash}}">
						
						<%
						paramIndex = 0
						for param in savedQuery.parameters:
						paramType = param.paramType
						%>
						<div class="form-group">
							<label for="sq{{queryIndex}}-param{{paramIndex}}">{{param.name}}</label>
							% if paramType == "text":
							<input type="text"
							% elif paramType == "select":
							<select multiple
							% elif paramType == "bool":
							<select
							% end
							% #if param.required: #todo add support for optional params
							required
							% #end
							id="sq{{queryIndex}}-param{{paramIndex}}" name="param{{paramIndex}}" class="form-control">
							% if paramType == "text":
							</input>
								% if param.allowMulti:
							<p class="form-tip"><em>Separate multiple entries with commas.</em><p>
								% end
							<% elif paramType == "select":
							for option in param.options:
							%>
								<option>{{option}}</option>
							% end
							</select>
							% if param.allowMulti:
							<p class="form-tip"><em>Hold <kbd>command</kbd> (Mac) or <kbd>control</kbd> (PC) to select multiple options.</em><p>
							% end
							% elif paramType == "bool":
								<option></option>
								<option>Yes</option>
								<option>No</option>
							</select>
							% end
						</div>
						
						<%
						paramIndex += 1
						end
						%>
						
						<input type="submit" class="btn btn-primary" value="Run Query">
					</form>
		 		</div>
			</div>
		</div>
	</div>
	
	<%
	queryIndex += 1
	end
	%>
</div>

% else:
<p>No saved queries found.</p>
% end


<h2>Custom Query</h2>

<div class="col-md-6 col-lg-6 no-gutter">
	<form data-toggle="validator" action="/data/{{dataset}}/custom-query/" method="post">
		<div class="form-group">
			<label for="customQuery">SQLite Query:</label>
			<textarea required id="customQuery" name="query" class="form-control" rows="3"></textarea>
		</div>
		<input type="submit" class="btn btn-primary" value="Run Query">
	</form>
</div>

% include(basePath + "app/templates/footer.tpl")
