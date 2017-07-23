# Webserver Stuff

from lib.bottle import Bottle, run, template, static_file, request

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	return template("templates/index.tpl")
	
@bottleApp.route("/data/<dataset:re:sessions|eno>")
def data(dataset):
	return template("templates/data.tpl", dataset=dataset, savedQueries=SavedQuery.loadAllForDataset(dataset))
	
@bottleApp.post("/data/<dataset:re:sessions|eno>/query")
def query(dataset):
	hashVal = int(request.forms.get("hash"))
	savedQueries = SavedQuery.loadAllForDataset(dataset)
	matchedQueries = [query for query in savedQueries if query.hash == hashVal]
	if len(matchedQueries) > 0:
		thisQuery = matchedQueries[0]
		return thisQuery.name
	else:
		return None
	
@bottleApp.route("/static/<filename:path>")
def static(filename):
	return static_file(filename, root="static/")
	

# Database Stuff

from os import listdir
import json

class SavedQuery(object):
	"""A prepared database query, loaded dynamically from JSON files in /saved-queries/"""
	
	def __init__(self, name = "", description = "", query = "", parameters = []):
		self.name = name
		self.description = description
		self.query = query
		self.parameters = parameters
	
	# Query declared as property so that setter can update hash
	@property
	def query(self):
		return self._query
	@query.setter
	def query(self, value):
		self._query = value
		self.hash = hash(value)
		
	def __str__(self):
		return "SavedQuery '{}' ({} parameters)".format(self.name, len(self.parameters))

	@classmethod
	def initFromJsonString(self, jsonString):
		try:
			parsedJson = json.loads(jsonString)
		except:
			print "Error loading saved query: couldn't parse json"
			return None
		name = parsedJson.get("name", "")
		description = parsedJson.get("description", "")
		query = parsedJson.get("query", "")
		parameters = parsedJson.get("parameters", [])
		# TODO add validation of each param
		if name == "" or query == "":
			print "Error loading saved query '{}': name and query are required".format(name)
			return None
		if len(parameters) != query.count("?"):
			print "Error loading saved query '{}': number of parameters ({}) must match number of placeholders in query ({})".format(name, len(parameters), query.count("?"))
			return None
		return SavedQuery(name=name, description=description, query=query, parameters=parameters)
		
	@staticmethod
	def loadAllForDataset(dataset):
		basePath = "saved-queries/" + dataset + "/"
		filesList = listdir(basePath)
		parsedQueries = []
		for thisFile in filesList:
			if thisFile.endswith(".json"):
				openFile = open(basePath + thisFile, "r")
				jsonString = openFile.read()
				openFile.close()
				thisQuery = SavedQuery.initFromJsonString(jsonString)
				# Make sure the query was parsed successfully and is different from others in the list
				if thisQuery:
					identicalQueries = [query for query in parsedQueries if int(query.hash) == int(thisQuery.hash)]
					if len(identicalQueries) < 1:
						parsedQueries.append(thisQuery)
					else:
						print "Error loading saved query '{}': identical query already loaded under name '{}'".format(thisQuery.name, identicalQueries[0].name)
		parsedQueries = sorted(parsedQueries, key=lambda k: k.name) # Alphabetize the list
		return parsedQueries

run(bottleApp, host="localhost", port=8888, debug=True, reloader=True)
