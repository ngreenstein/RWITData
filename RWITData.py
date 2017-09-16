#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === Globals ===

DEBUG = False
DEBUG = True

sessionsDb = None
enoDb = None

# === Webserver Stuff ===

from app.lib.bottle import Bottle, run, template, static_file, request
from shutil import copyfile
import os.path, tempfile, sys

FROZEN = getattr(sys, "frozen", False)

if FROZEN:
	DEBUG = False

basePath = ""
if FROZEN:
	basePath += os.path.dirname(sys.executable) + "/"

def makePath(localPath):
	return basePath + localPath

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	return template(makePath("app/templates/index.tpl"), basePath = basePath)
	
@bottleApp.route("/data/<dataset:re:sessions|eno>")
def data(dataset):
	return template(makePath("app/templates/data.tpl"), basePath = basePath, dataset=dataset, datasetName=datasetNames.get(dataset), savedQueries=SavedQuery.loadAllForDataset(dataset))
	
@bottleApp.post("/data/<dataset:re:sessions|eno>/query")
def query(dataset):
	return "Saved query execution not yet implemented."
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
	return template(makePath("app/templates/admin.tpl"), basePath = basePath, dataset=dataset, datasetName=datasetNames.get(dataset))
	
@bottleApp.post("/admin/<dataset:re:sessions|eno>/export")
def exp(dataset):
	terms = request.forms.get("exportTerms")
	if len(terms) > 0:
		terms = terms.split(", ")
	if dataset == "sessions":
		if request.forms.get("sqlite"):
			try:
				os.remove(makePath("app/download/temp-export.db"))
			except OSError:
				pass # If the file does not exist, don't worry about it
			try:
				copyfile(makePath("app/db/sessions.db"), makePath("app/download/temp-export.db"))
				# If filtering by terms, prune out irrelevant entries
				if len(terms) > 0:
					tempDb = SessionsDatabaseManager(makePath("app/download/temp-export.db"))
					termPlaceholders = ",".join("?" * len(terms))
					# Remove center sessions and associated entries
					centerQuery = "SELECT id, tutorRecordId, clientRecordId FROM centerSessions WHERE term NOT IN ({})".format(termPlaceholders);
					badCenterRows = tempDb.connection.execute(centerQuery, terms).fetchall()
					badCenterSessions, badTutorRecords, badClientRecords = [], [], []
					for sessionId, tutorRecordId, clientRecordId in badCenterRows:
						if sessionId:
							badCenterSessions.append(sessionId)
						if tutorRecordId:
							badTutorRecords.append(tutorRecordId)
						if clientRecordId:
							badClientRecords.append(clientRecordId)
					tempDb.connection.executemany("DELETE FROM centerSessions WHERE id = ?;", [(thisId,) for thisId in badCenterSessions])
					tempDb.connection.executemany("DELETE FROM tutorRecords WHERE id = ?;", [(thisId,) for thisId in badTutorRecords])
					tempDb.connection.executemany("DELETE FROM clientRecords WHERE id = ?;", [(thisId,) for thisId in badClientRecords])
					# Remove WA sessions
					waQuery = "SELECT id FROM writingAssistantSessions WHERE term NOT IN ({})".format(termPlaceholders);
					badWaSessions = [thisId[0] for thisId in tempDb.connection.execute(waQuery, terms).fetchall()]
					tempDb.connection.executemany("DELETE FROM writingAssistantSessions WHERE id = ?;", [(thisId,) for thisId in badWaSessions])
					# Remove extraneous people and tutorStubs
					# [TODO ngreenstein] See if there's a more compact way to do this
					allPeople = [thisId[0] for thisId in tempDb.connection.execute("SELECT id FROM people;").fetchall()]
					peopleToRemove = []
					for personId in allPeople:
						refCount = 0
						refCount += len(tempDb.connection.execute("SELECT id FROM centerSessions WHERE clientId = ?;", (personId,)).fetchall())
						refCount += len(tempDb.connection.execute("SELECT id FROM writingAssistantSessions WHERE tutorId = ?;", (personId,)).fetchall())
						if refCount <= 0:
							peopleToRemove.append(personId)
					tempDb.connection.executemany("DELETE FROM people WHERE id = ?;", [(thisId,) for thisId in peopleToRemove])
					allTutorStubs = [thisId[0] for thisId in tempDb.connection.execute("SELECT id FROM tutorStubs;").fetchall()]
					tutorStubsToRemove = []
					for tutorStubId in allTutorStubs:
						refCount = 0
						refCount += len(tempDb.connection.execute("SELECT id FROM centerSessions WHERE tutorId = ?;", (tutorStubId,)).fetchall())
						if refCount <= 0:
							tutorStubsToRemove.append(tutorStubId)
					tempDb.connection.executemany("DELETE FROM tutorStubs WHERE id = ?;", [(thisId,) for thisId in tutorStubsToRemove])
					tempDb.connection.commit()
				return static_file("temp-export.db", root = makePath("app/download/"), download = "RWITData.db")
			except Exception as error:
				print "An error occurred during export {}".format(error)
				return None
		elif request.forms.get("csv"):
			return "CSV file export not yet implemented. Please use the SQLite export function."
	else:
		return "E&O export not yet implemented."
	
@bottleApp.post("/admin/<dataset:re:sessions|eno>/import")
def imp(dataset):
	try:
		mode = ""
		if request.forms.get("replaceExisting"):
			mode = "replace"
		elif request.forms.get("addToExisting"):
			mode = "add"
		importFile = request.files.get("importFile")
		name, ext = os.path.splitext(importFile.filename)
		if ext not in (".csv", ".db", ".sqlite", ".sqlite3", ".db3"):
			return "BAD: invalid filetype"
		if os.fstat(importFile.file.fileno()).st_size > 100000000:
			return "BAD: file too large (more than 100MB)"
			
		tempFilePath = tempfile.gettempdir() + "temp-incoming-import" + ext
		importFile.save(tempFilePath, overwrite=True)
		
		global sessionsDb, enoDb
		
		# [TODO ngreenstein] See if there's a way to organize this a little more neatly.
		# At least use constants instead of string literals.
		if dataset == "sessions":
			if mode == "add":
				if ext == ".csv":
					sessionsDb.addFromCsv(tempFilePath)
				else: # All other extensions are sqlite
					sessionsDb.addFromSqlite(tempFilePath)
			elif mode == "replace":
				newDb = None
				if ext == ".csv":
					newDb = SessionsDatabaseManager.replaceFromCsv(tempFilePath)
				else: # All other extensions are sqlite
					newDb = SessionsDatabaseManager.replaceFromSqlite(tempFilePath)
				if newDb:
					sessionsDb.connection.close()
					sessionsDb = newDb
		elif dataset == "eno":
			return "E&O import is not yet implemented."
			if mode == "add":
				if ext == ".csv":
					enoDb.addFromCsv(tempFilePath)
				else: # All other extensions are sqlite
					enoDb.addFromSqlite(tempFilePath)
			elif mode == "replace":
				if ext == ".csv":
					EnoDatabaseManager.replaceFromCsv(tempFilePath)
				else: # All other extensions are sqlite
					EnoDatabaseManager.replaceFromSqlite(tempFilePath)
	
	except Exception as error:
		print "An error occurred during import {}".format(error)
	
	return "<p>Import {} data from {} in {} mode</p>".format(dataset, importFile.filename, mode)
	
@bottleApp.route("/about")
def about():
	return template(makePath("app/templates/about.tpl"), basePath = basePath)
	
@bottleApp.route("/static/<filename:path>")
def static(filename):
	return static_file(filename, root=makePath("app/static/"))

# The server only allows these two values for dataset; anything else 404s
datasetNames = {"sessions": "Session", "eno": "Education & Outreach"}
	
# === Database Stuff ===

from os import listdir, remove
import sqlite3, json, shutil, csv, re

class DatabaseManager(object):
	"""Keeps track of database connections and provides convenience methods for interacting with them"""
	
	masterPath = None
	
	def __init__(self, dbFile):
		self.connection = sqlite3.connect(dbFile)
		self.connection.text_factory = str
		
	def executeScript(self, script):
		self.connection.executescript(script)
		self.connection.commit()
	
	@classmethod
	def replaceFromCsv(cls, csvPath):
		# Make an empty database, use the addFromCsv() machinery to load the CSV data into it,
		# and use the the replaceFromSqlite() machinery to get rid of the old database.
		tempPath = tempfile.gettempdir() + "temp-incoming-import.db"
		# Make sure nothing is lingering; we want a fresh database
		try:
			os.remove(tempPath)
		except OSError:
			pass # If the file does not exist, don't worry about it
		tempDb = cls(dbPath = tempPath)
		tempDb.connection.text_factory = str
		schemaFile = open(makePath("app/db/sessions-schema.sql"), "r")
		createScript = schemaFile.read()
		schemaFile.close()
		tempDb.connection.executescript(createScript)
		tempDb.addFromCsv(csvPath)
		tempDb.connection.close()
		return cls.replaceFromSqlite(tempPath)
	
	@classmethod
	def replaceFromSqlite(cls, sqlitePath):
		incomingDb = cls(dbPath = sqlitePath)
		# Validate incoming schema against stored master (equivalent to validating against current database
		# schema because that is validated against stored master at startup).
		if not incomingDb.validateOwnSchema():
			print "BAD: Incoming database schema invalid."
			incomingDb.connection.close()
			os.remove(sqlitePath)
			return False
		else:
			# If the incoming database is valid, delete the old one and move the new one into its proper place
			os.remove(cls.masterPath)
			shutil.move(sqlitePath, cls.masterPath)
			return cls()
		
	def addFromCsv(self, csvPath):
		pass
		
	def addFromSqlite(self, sqlitePath):
		# Validate incoming schema against stored master (equivalent to validating against current database
		# schema because that is validated against stored master at startup).
		incomingDb = self.__class__(dbPath = sqlitePath)
		if not incomingDb.validateOwnSchema():
			print "BAD: Incoming database schema invalid."
			incomingDb.connection.close()
			try:
				os.remove(sqlitePath)
			except OSError:
				pass # If the file does not exist, don't worry about it.
			return False
		else:
			# If the incoming database is valid, walk through all its tables and add each row to the correspondnig table
			# of the current database. Any duplicates between incoming and current db (or otherwise malformed rows)
			# are ignored. Should be just duplicates in most cases, though, because schema has been validated to enforce
			# other proper behavior.
			incomingDb.connection.close()
			self.connection.execute("ATTACH '{}' AS incomingDb;".format(sqlitePath))
			for (thisTable,) in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"):
				self.connection.execute("INSERT OR IGNORE INTO {} SELECT * FROM incomingDb.{};".format(thisTable, thisTable))
			self.connection.execute("DETACH incomingDb;")
			self.connection.commit()
	
	# Dumps the schema of a database connection into a string (just for use in comparing schemas; not actually meant to be stored)
	@staticmethod
	def serializeSchema(connection):
		tables = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' OR type = 'trigger' ORDER BY name;")
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
		tempConnection.text_factory = str
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
	
	masterPath = makePath("app/db/sessions.db")
	
	def __init__(self, dbPath = masterPath):
		return super(self.__class__, self).__init__(dbPath)
		
	def validateOwnSchema(self):
		return super(self.__class__, self).validateSchema(makePath("app/db/sessions-schema.sql"))
	
	# RWIT Online's CSV export only identifies tutors by name. More info on them is
	# available if they've been clients or WAs, but not all tutors have been.
	def enrichTutorData(self):
		pass
		# maybe do as db trigger instead?
	
	def addFromCsv(self, csvPath):
		
		# Read the CSV file
		csvFile = open(csvPath, "r")
		csvReader = csv.DictReader(csvFile)
		
		# A few utility functions
		
		#	From an array of bindings, produce a list of columns (e.g. "name, status, deptClass")
		def colStringFromBindings(bindings):
			return ", ".join(pair[1] for pair in bindings)
		#	From an array of bindings, produce a list of column placeholders (e.g. ":name, :status, :deptClass")
		def placeholderStringFromBindings(bindings):
			return ":" + ", :".join(pair[1] for pair in bindings)
		#	From an array of bindings and a CSV row, produce a dict of SQLite column names to values
		def valuesDictFromBindingsAndCsvRow(bindings, csvRow):
			values = {}
			for pair in bindings:
				values[pair[1]] = csvRow.get(pair[0])
			return values
		#	If all values in a dict are empty or zero-length strings, return False. Otherwise, return True.
		def dictHasSomeValue(searchDict):
			for val in searchDict.values():
				if val:
					try:
						if len(val) < 1: return False
					except Exception:
						pass
					return True
			return False
		# Reorder term names from RWIT Online (e.g. "X17" -> "17X")
		def reorderTermNameInDict(dict, key = "term"):
			originalTerm = dict.get(key)
			regex = re.search(r"(F|W|S|X)(\d{2})", originalTerm)
			if len(regex.groups()) > 0:
				quarter = regex.group(1)
				year = regex.group(2)
				reorderedTerm = year + quarter
				dict[key] = reorderedTerm
		
		# Do the actual import legwork
		
		# The system used here is largely based on arrays of tuples providing 'bindings' for each type of entity
		# we consider when importing. This is more verbose than other methods, but safer and more maintainable:
		# it allows new columns to be added (and old columns to be reordered) in both the RWIT Online CSV export
		# and the RWITData schemas without breaking things. It also makes it easy to rebind and make other edits
		# without having to keep track of a bunch of identical-looking '?' placeholders.
		
		# To use this system, create your bindings (an array of tuples where the first string is a CSV column heading
		# and the second string is a SQLite column name). Make sure all columns in a given table are included in
		# bindings, even things like foreign keys that aren’t imported from CSV columns (just use None as the first
		# item in the tuple and the SQLite column name as the second item). Then use the utility functions above to
		# produce a string representing each db column and a string of placeholders for each value. Finally, use
		# string formatting to build your SQL query with column names and placeholders (but no values yet), e.g.
		# `"INSERT OR IGNORE INTO people({}) VALUES ({});".format(clientCols, clientPlaceholders)`. Later, use the
		# valuesDictFromBindingsAndCsvRow() utility function to pull values from the CSV file. Do any other work you
		# need (e.g. adding foreign keys) and then run the query with the values dict as the second argument.
		
		#	Set up all the bindings
		
		centerSessionBindings = [(None, "clientId"),
								   (None, "tutorId"),
								   ("session_type", "type"),
								   ("term", "term"),
								   ("start_time", "startTime"),
								   ("stop_time", "stopTime"),
								   ("session_created_at", "creationTime"),
								   ("session_updated_at", "updateTime"),
								   ("state", "state"),
								   (None, "tutorRecordId"),
								   (None, "clientRecordId")]
		centerSessionCols = colStringFromBindings(centerSessionBindings)
		centerSessionPlaceholders = placeholderStringFromBindings(centerSessionBindings)
		centerSessionInsertQuery = "INSERT INTO centerSessions({}) VALUES ({});".format(centerSessionCols, centerSessionPlaceholders)
		waSessionBindings = [(None, "tutorId"),
							   ("session_type", "type"),
							   ("term", "term"),
							   ("start_time", "date"),
							   ("session_created_at", "creationTime"),
							   ("session_updated_at", "updateTime"),
							   ("hours", "hours"),
							   ("attendees", "attendees"),
							   ("assignment", "assignment"),
							   ("pages_assigned", "pagesAssigned"),
							   ("pages_reviewed", "pagesReviewed"),
							   ("tutor_feedback", "tutorFeedback")]
		waSessionCols = colStringFromBindings(waSessionBindings)
		waSessionPlaceholders = placeholderStringFromBindings(waSessionBindings)
		waSessionInsertQuery = "INSERT INTO writingAssistantSessions({}) VALUES ({});".format(waSessionCols, waSessionPlaceholders)
		clientBindings = [("client_name", "name"),
							("client_status", "status"),
							("client_deptclass", "deptClass"),
							("client_majors", "majors"),
							("client_minors", "minors"),
							("client_other_major_minor", "otherMajorMinor"),
							("client_modifieds", "modifieds"),
							("client_graduate_programs", "graduatePrograms"),
							("client_first_language", "firstLanguage"),
							("client_fluent_speaking", "fluentSpeaking"),
							("client_fluent_reading", "fluentReading"),
							("client_fluent_writing", "fluentWriting")]
		clientCols = colStringFromBindings(clientBindings)
		clientPlaceholders = placeholderStringFromBindings(clientBindings)
		clientInsertQuery = "INSERT OR IGNORE INTO people({}) VALUES ({});".format(clientCols, clientPlaceholders)
		clientFindQuery = "SELECT id FROM people WHERE name = ? and deptClass = ?;"
		tutorStubInsertQuery = "INSERT OR IGNORE INTO tutorStubs('name') VALUES (?);"
		tutorStubFindQuery = "SELECT id FROM tutorStubs WHERE name = ?;"
		clientRecordBindings = [(None, "clientId"),
								 ("client_global_goal_mets", "globalGoalsMet"),
								 ("client_local_goal_mets", "localGoalsMet"),
								 ("client_feedback", "feedback"),
								 ("client_suggestions", "suggestions"),
								 ("The tutor's comments and suggestions were useful:", "useful"),
								 ("The tutor's interpersonal style was appropriate:", "appropriate"),
								 ("How much did you learn in your session that you might apply to future assignments?", "learned"),
								 ("Will you use RWIT again?", "again"),
								 ("Would you recommend RWIT to your friends?", "recommend")]
		clientRecordCols = colStringFromBindings(clientRecordBindings)
		clientRecordPlaceholders = placeholderStringFromBindings(clientRecordBindings)
		clientRecordInsertQuery = "INSERT INTO clientRecords({}) VALUES ({});".format(clientRecordCols, clientRecordPlaceholders)
		tutorRecordBindings = [(None, "tutorId"),
								("primary_document_type", "primaryDocumentType"),
								("other_primary_document_type", "otherPrimaryDocumentType"),
								("primary_document_due_date", "dueDate"),
								("document_types", "documentTypes"),
								("document_categories", "documentCategories"),
								("document_languages", "documentLanguages"),
								("writing_phases", "writingPhases"),
								("global_goals", "globalGoals"),
								("global_goal_mets", "globalGoalsMet"),
								("local_goals", "localGoals"),
								("local_goal_mets", "localGoalsMet"),
								("outcomes", "outcomes"),
								("strategies", "strategies"),
								("tutor_feedback", "tutorFeedback"),
								("tutor_self_assessment", "tutorSelfAssess")]
		tutorRecordCols = colStringFromBindings(tutorRecordBindings)
		tutorRecordPlaceholders = placeholderStringFromBindings(tutorRecordBindings)
		tutorRecordInsertQuery = "INSERT INTO tutorRecords({}) VALUES ({});".format(tutorRecordCols, tutorRecordPlaceholders)
		
		# 	Loop through CSV rows and import each one
		
		for csvRow in csvReader:
			
			# Writing assistant sessions are pretty different, so just handle the two cases separately.
			# `attendees` has some content for WA sessions, even if it's just "[]", but it's blank on center sessions
			# [TODO ngreenstein] Verify above. Showing no recent WA sessions except during 17S and 15S.
			if len(csvRow.get("attendees")) > 0:
				
				waSessionVals = valuesDictFromBindingsAndCsvRow(waSessionBindings, csvRow)
				reorderTermNameInDict(waSessionVals)
				# For WA sessions, the info in the client fields actually describes the tutor,
				# so treat tutors as real people instead of stubs.
				tutorVals = valuesDictFromBindingsAndCsvRow(clientBindings, csvRow)
				# Store the tutor info
				self.connection.execute(clientInsertQuery, tutorVals)
				# Find the matching tutor's id (can't just use `lastrowid` because duplicate people are ignored, not inserted)
				tutorId = self.connection.execute(clientFindQuery, (tutorVals.get("name"), tutorVals.get("deptClass"))).fetchone()[0]
				# Fill in the session's tutorId fkey
				waSessionVals["tutorId"] = tutorId
				# Store the session info
				self.connection.execute(waSessionInsertQuery, waSessionVals)
				
			else:
				
				# Assemble basic values from bindings/CSV row
				centerSessionVals = valuesDictFromBindingsAndCsvRow(centerSessionBindings, csvRow)
				reorderTermNameInDict(centerSessionVals)
				clientVals = valuesDictFromBindingsAndCsvRow(clientBindings, csvRow)
				tutorName = csvRow.get("tutor_name")
				clientRecordVals = valuesDictFromBindingsAndCsvRow(clientRecordBindings, csvRow)
				tutorRecordVals = valuesDictFromBindingsAndCsvRow(tutorRecordBindings, csvRow)
				
				# Store the client info and tutor stub, then grab ids
				self.connection.execute(clientInsertQuery, clientVals)
				clientId = self.connection.execute(clientFindQuery, (clientVals.get("name"), clientVals.get("deptClass"))).fetchone()[0]
				centerSessionVals["clientId"] = clientId
				tutorStubId = -1
				if len(tutorName) > 0: # Cancelled center sessions have no tutor
					self.connection.execute(tutorStubInsertQuery, (tutorName,))
					tutorStubId = self.connection.execute(tutorStubFindQuery, (tutorName,)).fetchone()[0]
					centerSessionVals["tutorId"] = tutorStubId
				
				# It's possible for client and tutor records to be incomplete. Store them if at least one field has a value;
				# discard if everything is blank.
				if dictHasSomeValue(clientRecordVals):
					clientRecordVals["clientId"] = clientId
					clientRecordId = self.connection.execute(clientRecordInsertQuery, clientRecordVals).lastrowid
					centerSessionVals["clientRecordId"] = clientRecordId
				if dictHasSomeValue(tutorRecordVals):
					if tutorStubId >= 0:
						tutorRecordVals["tutorId"] = tutorStubId
					tutorRecordId = self.connection.execute(tutorRecordInsertQuery, tutorRecordVals).lastrowid
					centerSessionVals["tutorRecordId"] = tutorRecordId
				
				# Store the session info
				self.connection.execute(centerSessionInsertQuery, centerSessionVals)
		
		# Cleanup
		self.connection.commit()
		csvFile.close()
		
		return self
	
class EnoDatabaseManager(DatabaseManager):
	"""Keeps track of education & outreach database connections and provides convenience methods for interacting with them"""
	
	masterPath = makePath("app/db/eno.db")
	
	def __init__(self, dbPath = masterPath):
		return super(self.__class__, self).__init__(dbPath)
		
	def validateOwnSchema(self):
		return super(self.__class__, self).validateSchema(makePath("app/db/eno-schema.sql"))

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
		basePath = makePath("app/saved-queries/") + dataset + "/"
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

dbFiles = listdir(makePath("app/db/"))

sessionsDb = SessionsDatabaseManager()
enoDb = EnoDatabaseManager()

if not "sessions.db" in dbFiles:
	try:
		openFile = open(makePath("app/db/sessions-schema.sql"), "r")
		script = openFile.read()
		openFile.close()
		sessionsDb.executeScript(script)
	except Exception as error:
		print "An error occurred creating the sessions database: {}".format(error)
		
if not "eno.db" in dbFiles:
	try:
		openFile = open(makePath("app/db/eno-schema.sql"), "r")
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

if not DEBUG:
	welcomeString = "\n\n"
	welcomeString += "========== WELCOME TO RWITData! ==========\n"
	welcomeString += "== To begin, open http://localhost:8888 ==\n"
	welcomeString += "== in your web browser. When finished,  ==\n"
	welcomeString += "== simply close this window.            ==\n"
	welcomeString += "==========================================\n"
	print welcomeString
					  

run(bottleApp, host="localhost", port=8888, debug=DEBUG, reloader=DEBUG)

sessionsDb.connection.close()
enoDb.connection.close()