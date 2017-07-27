#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === Webserver Stuff ===

from lib.bottle import Bottle, run, template, static_file, request

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	return template("templates/index.tpl")
	
@bottleApp.route("/data/<dataset:re:sessions|eno>")
def data(dataset):
	return template("templates/data.tpl", dataset=dataset, datasetName=datasetNames.get(dataset), savedQueries=SavedQuery.loadAllForDataset(dataset))
	
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

@bottleApp.route("/admin/<dataset:re:sessions|eno>")
def admin(dataset):
	return template("templates/admin.tpl", dataset=dataset, datasetName=datasetNames.get(dataset))
	
@bottleApp.post("/admin/<dataset:re:sessions|eno>/export")
def export(dataset):
	format = ""
	if request.forms.get("sqlite"):
		format = "sqlite"
	elif request.forms.get("csv"):
		format = "csv"
	return "<p>Export {} data for terms {} as {}</p>".format(dataset, request.forms.get("exportTerms"), format)
	
@bottleApp.post("/admin/<dataset:re:sessions|eno>/import")
def imp(dataset):
	mode = ""
	if request.forms.get("replaceExisting"):
		mode = "replace"
	elif request.forms.get("addToExisting"):
		mode = "add"
	importFile = request.files.get("importFile")
	return "<p>Import {} data from {} in {} mode</p>".format(dataset, importFile.filename, mode)
	
@bottleApp.route("/about")
def about():
	return template("templates/about.tpl")
	
@bottleApp.route("/static/<filename:path>")
def static(filename):
	return static_file(filename, root="static/")

# The server only allows these two values for dataset; anything else 404s
datasetNames = {"sessions": "Session", "eno": "Education & Outreach"}
	
# === Database Stuff ===

from os import listdir
import sqlite3, json

class DatabaseManager(object):
	"""Keeps track of database connections and provides convenience methods for interacting with them"""
	
	def __init__(self, dbFile):
		self.connection = sqlite3.connect(dbFile)
		
	def executeScript(self, script):
		self.connection.executescript(script)
		self.connection.commit()
		
	def importFromCsv(self, csvPath):
		pass
		
	def importFromSqlite(self, sqlitePath, replace=False):
		pass
	
	# Dumps the schema of a database connection into a string (just for use in comparing schemas; not actually meant to be stored)
	@staticmethod
	def serializeSchema(connection):
		tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
		serialized = ""
		for (tableName,) in tables:
			serialized += str(tableName) + "\n"
			columns = connection.execute("pragma table_info('{}')".format(tableName)).fetchall()
			for column in columns:
				serialized += str(column) + "\n"
		return serialized
	
	# Comapres the schema of an instance's database with the schema specified in the sourceSchema file
	def validateSchema(self, sourceSchema):
		tempConnection = sqlite3.connect(":memory:")
		openFile = open(sourceSchema, "r")
		createScript = openFile.read()
		openFile.close()
		tempConnection.executescript(createScript)
		validSerialized = self.__class__.serializeSchema(tempConnection)
		testSerialized = self.__class__.serializeSchema(self.connection)
		tempConnection.close()
		return testSerialized == validSerialized
		
	def validateOwnSchema(self):
		pass
		
class SessionsDatabaseManager(DatabaseManager):
	"""Keeps track of sessions database connections and provides convenience methods for interacting with them"""
	
	def __init__(self):
		return super(self.__class__, self).__init__("db/sessions.db")
		
	def validateOwnSchema(self):
		return super(self.__class__, self).validateSchema("db/sessions-schema.sql")
	
class EnoDatabaseManager(DatabaseManager):
	"""Keeps track of education & outreach database connections and provides convenience methods for interacting with them"""
	
	def __init__(self):
		return super(self.__class__, self).__init__("db/eno.db")
		
	def validateOwnSchema(self):
		return super(self.__class__, self).validateSchema("db/eno-schema.sql")

class SavedQuery(object):
	"""A prepared database query, loaded dynamically from JSON files in /saved-queries/"""
	
	def __init__(self, name = "", description = "", query = "", parameters = []):
		self.name = name
		self.description = description
		self.query = query
		self.parameters = parameters
	
	# query declared as property so that setter can update hash
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


# Look for the databases and create them if they do not exist

dbFiles = listdir("db/")

sessionsDb = SessionsDatabaseManager()
enoDb = EnoDatabaseManager()

if not "sessions.db" in dbFiles:
	try:
		openFile = open("db/sessions-schema.sql", "r")
		script = openFile.read()
		openFile.close()
		sessionsDb.executeScript(script)
	except Exception as error:
		print "An error occurred creating the sessions database: {}".format(error)
		
if not "eno.db" in dbFiles:
	try:
		openFile = open("db/eno-schema.sql", "r")
		script = openFile.read()
		openFile.close()
		enoDb.executeScript(script)
	except Exception as error:
		print "An error occurred creating the education & outreach database: {}".format(error)

try:
	if not sessionsDb.validateOwnSchema():
		print "Error: sessions database schema is invalid"
except Exception as error:
	print "An error occurred validating the sessions database schema: {}".format(error)

try:
	if not enoDb.validateOwnSchema():
		print "Error: education & outreach database schema is invalid"
except Exception as error:
	print "An error occurred validating the education and outreach database schema: {}".format(error)

run(bottleApp, host="localhost", port=8888, debug=True, reloader=True)

sessionsDb.connection.close()
enoDb.connection.close()