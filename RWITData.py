from lib.bottle import Bottle, run

bottleApp = Bottle()
	
run(bottleApp, host="localhost", port=8888, debug=True, reloader=True)