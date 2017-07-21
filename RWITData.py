from lib.bottle import Bottle, run, template

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	return template("templates/index.tpl")
	
run(bottleApp, host="localhost", port=8888, debug=True, reloader=True)