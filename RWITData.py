from lib.bottle import Bottle, run, template, static_file

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	return template("templates/index.tpl")
	
@bottleApp.route("/data/<dataset:re:sessions|eno>")
def data(dataset):
	return template("templates/data.tpl", dataset=dataset)
	
@bottleApp.route("/static/<filename:path>")
def static(filename):
	return static_file(filename, root="static/")
	
run(bottleApp, host="localhost", port=8888, debug=True, reloader=True)