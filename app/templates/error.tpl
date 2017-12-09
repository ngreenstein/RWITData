% include(basePath + "app/templates/header.tpl", title="Error")

<h1>An Error Occurred</h1>

<p>This operation encountered the following error:</p>

<pre class="danger">{{shortMessage}}</pre>

<div class="form-group">
	<a class="btn btn-primary" id="back-button" href="/">Go Back</a>
</div>

% if defined("longMessage") and longMessage:

<p>Additional information:</p>

<pre>{{longMessage}}</pre>

% end

% include(basePath + "app/templates/footer.tpl", scripts = ["/static/error.js"])