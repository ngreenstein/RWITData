from lib.bottle import Bottle, run, template, static_file

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	return template("templates/index.tpl")
	
@bottleApp.route("/static/<filename:path>")
def static(filename):
	return static_file(filename, root="static/")
	
run(bottleApp, host="localhost", port=8080, debug=True, reloader=True)