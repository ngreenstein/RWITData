<%
# The server only allows these two values for dataset; anything else 404s
datasetNames = {"sessions": "Session", "eno": "Education & Outreach"}
datasetName = datasetNames[dataset]
pageTitle = datasetName + " Data"

include("templates/header.tpl", title=pageTitle)
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
				 	
					<form data-toggle="validator" action="/data/sessions/query" method="post">
						
						<input type="hidden" name="hash" value="{{savedQuery.hash}}">
						
						<%
						paramIndex = 0
						for param in savedQuery.parameters:
						paramType = param.get("type")
						%>
						<div class="form-group">
							<label for="sq{{queryIndex}}-param{{paramIndex}}">{{param.get("name")}}</label>
							% if paramType == "text":
							<input
							% elif paramType == "select":
							<select multiple
							% elif paramType == "bool":
							<select
							% end
							% if param.get("required"):
							required
							% end
							id="sq{{queryIndex}}-param{{paramIndex}}" name="param{{paramIndex}}" class="form-control">
							% if paramType == "text":
							</input>
							<% elif paramType == "select":
							for option in param.get("options", []):
							%>
								<option>{{option}}</option>
							% end
							</select>
							<p class="multi-select-tip"><em>Hold <kbd>command</kbd> (Mac) or <kbd>control</kbd> (PC) to select multiple options.</em><p>
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
						
						<button type="submit" class="btn btn-primary">Run Query</button>
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
<p>coming soon</p>

% include("templates/footer.tpl")
