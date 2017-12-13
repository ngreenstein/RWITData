#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === Globals ===

DEBUG = False
DEBUG = True

sessionsDb = None
enoDb = None

# === Webserver Stuff ===

from app.lib.bottle import Bottle, run, template, static_file, request, redirect
from shutil import copyfile
import os, tempfile, sys, csv

FROZEN = getattr(sys, "frozen", False)

if FROZEN:
	DEBUG = False

basePath = ""
if FROZEN:
	basePath += os.path.dirname(sys.executable) + "/"
	
startupError = (None, None)

def makePath(localPath):
	return basePath + localPath

bottleApp = Bottle()

@bottleApp.route("/")
def index():
	# If an error occured during startup, show it the fist time the homepage is loaded.
	global startupError
	alert = None
	if startupError[0]:
		shortMsg = startupError[0]
		alert = ("<p><strong>Error starting RWITData:</strong> '{}'.</p>".format(shortMsg),)
		longMsg = None
		if len(startupError) > 1:
			longMsg = str(startupError[1])
			alert = (alert[0], longMsg)
		startupError = (None, None)
	return template(makePath("app/templates/index.tpl"), basePath = basePath, errors = [alert])
	
@bottleApp.route("/data/<dataset:re:sessions|eno>/")
def data(dataset):
	results = SavedQuery.loadAllForDataset(dataset)
	queries = results[0]
	errors = results[1]
	return template(makePath("app/templates/data.tpl"), basePath = basePath, dataset=dataset, datasetName=datasetNames.get(dataset), savedQueries=queries, errors = errors)
	
@bottleApp.post("/data/<dataset:re:sessions|eno>/saved-query/")
def savedQuery(dataset):
	hashVal = int(request.forms.get("hash"))
	savedQueries = SavedQuery.loadAllForDataset(dataset)[0]
	matchedQueries = [query for query in savedQueries if query.hash == hashVal]
	if len(matchedQueries) > 0:
		thisQuery = matchedQueries[0]
		i = 0
		for param in thisQuery.parameters:
			param.values = request.forms.getall("param" + str(i))
			i += 1
		paramValidation = thisQuery.validateParamValues()
		if len(paramValidation) > 0:
			shortMsg = "Unable to execute saved query '{}': invalid parameter values.".format(thisQuery.name)
			return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg, longMessage = "\n".join(paramValidation))
		try:
			db = sessionsDb
			if dataset == "eno": db = enoDb
			# print thisQuery.prepQuery()
			# print thisQuery.prepValues()
			cursor = db.connection.cursor()
			cursor.execute(thisQuery.prepQuery(), thisQuery.prepValues())
			description = []
			if cursor.description:
				description = [col[0] for col in cursor.description]
			results = cursor.fetchall()
			csvPath, resultsHash = DatabaseManager.hashAndSaveResults(results, description)
			return template(makePath("app/templates/results.tpl"), basePath = basePath, queryTitle = thisQuery.name, results = results, resultsHash = resultsHash, rowHeads = description)
		except Exception as error:
			shortMsg = "Unable to execute saved query '{}'.".format(thisQuery.name)
			return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg, longMessage = str(error))
	else:
		shortMsg = "The requested saved query was not found."
		return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg)

@bottleApp.post("/data/<dataset:re:sessions|eno>/custom-query/")
def customQuery(dataset):
	try:
		query = request.forms.get("query")
		db = sessionsDb
		if dataset == "eno": db = enoDb
		# Commit anything done before this starts so we can rollback afterwards without losing anything we might have wanted to keep
		cursor = db.connection.cursor()
		# todo better handling of errors when running sql; make access read-only if possible
		cursor.execute(query)
		description = []
		if cursor.description:
			description = [col[0] for col in cursor.description]
		results = cursor.fetchall()
		csvPath, resultsHash = DatabaseManager.hashAndSaveResults(results, description)
		return template(makePath("app/templates/results.tpl"), basePath = basePath, queryTitle = "Custom Query", results = results, resultsHash = resultsHash, rowHeads = description)
	except Exception as error:
		shortMsg = "Unable to execute custom query."
		return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg, longMessage = str(error))
	
@bottleApp.route("/data/<dataset:re:sessions|eno>/export-results/<resultsHash>/")
def exportResults(dataset, resultsHash):
	resultsPath = makePath("app/download/results-{}.csv".format(resultsHash))
	if os.path.isfile(resultsPath):
		return static_file("results-{}.csv".format(resultsHash), root = makePath("app/download/"), download = "QueryResults.csv")
	else:
		errMsg = "Unable to export results. Try running your query again."
		return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = errMsg)

@bottleApp.route("/admin/<dataset:re:sessions|eno>/")
def admin(dataset):
	return template(makePath("app/templates/admin.tpl/"), basePath = basePath, dataset = dataset, datasetName = datasetNames.get(dataset))
	
@bottleApp.post("/admin/<dataset:re:sessions|eno>/export/")
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
				shortMsg = "Unable to complete export."
				return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg, longMessage = str(error))
		elif request.forms.get("csv"):
			return "CSV file export not yet implemented. Please use the SQLite export function."
	else:
		return "E&O export not yet implemented."
	
@bottleApp.post("/admin/<dataset:re:sessions|eno>/import/")
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
			shortMsg = "Unable to import from '{}' because filetype is not CSV or SQLite. Try another file.".format(importFile.filename)
			return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg)
		if os.fstat(importFile.file.fileno()).st_size > 100000000:
			shortMsg = "Unable to import from '{}' because file is larger than 100MB. Try another file.".format(importFile.filename)
			return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg)
			
		tempFilePath = tempfile.gettempdir() + "/temp-incoming-import" + ext
		importFile.save(tempFilePath, overwrite=True)
		
		global sessionsDb, enoDb
		
		# [TODO ngreenstein] See if there's a way to organize this a little more neatly.
		# At least use constants instead of string literals.
		if dataset == "sessions":
			if mode == "add":
				outcome = None
				if ext == ".csv":
					outcome = sessionsDb.addFromCsv(tempFilePath)
				else: # All other extensions are sqlite
					outcome = sessionsDb.addFromSqlite(tempFilePath)
				if not isinstance(outcome, DatabaseManager):
					return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = outcome[0], longMessage = outcome[1])
			elif mode == "replace":
				newDb = None
				if ext == ".csv":
					newDb = SessionsDatabaseManager.replaceFromCsv(tempFilePath)
				else: # All other extensions are sqlite
					newDb = SessionsDatabaseManager.replaceFromSqlite(tempFilePath)
				if isinstance(newDb, DatabaseManager):
					sessionsDb.connection.close()
					sessionsDb = newDb
				else:
					return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = newDb[0], longMessage = newDb[1])
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
		shortMsg = "Unable to complete import."
		return template(makePath("app/templates/error.tpl"), basePath = basePath, shortMessage = shortMsg, longMessage = str(error))
	
	successAlert = ("Successfully {} data from '{}'.".format("added" if mode == "add" else "replaced", importFile.filename), "success")
	return template(makePath("app/templates/admin.tpl/"), basePath = basePath, dataset = dataset, datasetName = datasetNames.get(dataset), alerts = [successAlert])
	
@bottleApp.route("/about/")
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
		tempPath = tempfile.gettempdir() + "/temp-incoming-import.db"
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
		addResult = tempDb.addFromCsv(csvPath) # Captures errors on individual rows but recovers and keeps going
		tempDb.connection.close()
		replaceResult = cls.replaceFromSqlite(tempPath) # Either succeeds or fails
		
		# Kinda messy but allows reporting of errors on addFromCSV, replaceFromSqlite, or both.
		addErrored = isinstance(addResult, tuple)
		replaceErrored = isinstance(replaceResult, tuple)
		shortMsg = ""
		longMsg = ""
		if addErrored and replaceErrored:
			shortMsg = "Unable to replace database from CSV file '{}' for the following reason: '{}'.".format(os.path.basename(csvPath), replaceResult[1])
			longMsg = "Additionally, the following error(s) occurred while processing the CSV's content:\n" + addResult[1]
		elif replaceErrored:
			shortMsg = "Unable to replace database from CSV file '{}'.".format(os.path.basename(csvPath))
			longMsg = replaceResult[1]
		elif addErrored:
			shortMsg = "Successfully replaced database from CSV file '{}', but the following error(s) occurred while processing the CSV's content."
			longMsg = addResult[1]
		if not addErrored and not replaceErrored:
			return cls()
		return (shortMsg, longMsg)
	
	@classmethod
	# Returns a tuple (shortMsg, longMsg) for error or its class if successful
	def replaceFromSqlite(cls, sqlitePath):
		incomingDb = cls(dbPath = sqlitePath)
		# Validate incoming schema against stored master (equivalent to validating against current database
		# schema because that is validated against stored master at startup).
		if not incomingDb.validateOwnSchema():
			incomingDb.connection.close()
			os.remove(sqlitePath)
			shortMsg = "Unable to replace database from file '{}'.".format(os.path.basename(sqlitePath))
			longMsg = "Incoming database schema is invalid."
			return (shortMsg, longMsg)
		else:
			# If the incoming database is valid, delete the old one and move the new one into its proper place
			try:
				os.remove(cls.masterPath)
				shutil.move(sqlitePath, cls.masterPath)
				return cls()
			except Exception as error:
				shortMsg = "Unable to replace database from file '{}'.".format(os.path.basename(sqlitePath))
				return (shortMsg, str(error))
		
	def addFromCsv(self, csvPath):
		pass
		# Subclasses should return themselves for fully successful operations,
		# or an error tuple for operations where some error(s) occurred
	
	# Returns itself if successful or an error tuple if not
	def addFromSqlite(self, sqlitePath):
		# Validate incoming schema against stored master (equivalent to validating against current database
		# schema because that is validated against stored master at startup).
		incomingDb = self.__class__(dbPath = sqlitePath)
		if not incomingDb.validateOwnSchema():
			incomingDb.connection.close()
			try:
				os.remove(sqlitePath)
			except OSError:
				pass # If the file does not exist, don't worry about it.
			return ("Unable to add data from SQLite file '{}'.".format(os.path.basename(sqlitePath)), "Incoming database schema invalid.")
		else:
			# If the incoming database is valid, walk through all its tables and add each row to the correspondnig table
			# of the current database. Any duplicates between incoming and current db (or otherwise malformed rows)
			# are ignored. Should be just duplicates in most cases, though, because schema has been validated to enforce
			# other proper behavior.
			try:
				incomingDb.connection.close()
				self.connection.execute("ATTACH '{}' AS incomingDb;".format(sqlitePath))
				for (thisTable,) in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"):
					self.connection.execute("INSERT OR IGNORE INTO {} SELECT * FROM incomingDb.{};".format(thisTable, thisTable))
				self.connection.execute("DETACH incomingDb;")
				self.connection.commit()
			except Exception as error:
				return ("Unable to add data from SQLite file '{}'.".format(os.path.basename(sqlitePath)), str(error))
				
			return self
	
	# Dump a CSV copy of a results list, identified by hash, into a temporary folder.
	# CSV files are later served via the /export-results/ endpoint.
	@staticmethod
	def hashAndSaveResults(results = [], headers = ""):
		resultsHash = hash(str(headers)+str(results))
		filePath = makePath("app/download/results-" + str(resultsHash) + ".csv")
		with open(filePath, "wb") as file:
			writer = csv.writer(file)
			writer.writerow(headers)
			writer.writerows(results)
		return (filePath, resultsHash)
	
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
	
	# TODO De-duplication. Don't let add imports create duplicate entries if, e.g.,
	# 15F thru 16F is already in the db and someone and someone adds 16F thru 17F.
	# Is there a reason we aren't using RWIT Online's `session_id` for pkey and uniquing
	# that way? If there aren't problems with that, it might get us most of the way there.
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
		# 	Reorder term names from RWIT Online (e.g. "X17" -> "17X")
		def reorderTermNameInDict(dict, key = "term"):
			originalTerm = dict.get(key)
			regex = re.search(r"(F|W|S|X)(\d{2})", originalTerm)
			if len(regex.groups()) > 0:
				quarter = regex.group(1)
				year = regex.group(2)
				reorderedTerm = year + quarter
				dict[key] = reorderedTerm
		# 	Replace textual values with a corresponding quantitative value based on position in a list
		#	e.g. "No" -> 1, "Maybe" -> 2, "Yes" -> 3 for ("No", "Maybe", "Yes")
		def replaceQualitativeWithQuantitativeByPosition(dict, keys, positions):
			for key in keys:
				qualVal = dict.get(key)
				if qualVal and qualVal in positions:
					dict[key] = positions.index(qualVal) + 1
		
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
		clientRecordAgreeQual = ("Strongly Disagree", "Disagree", "Agree", "Strongly Agree")
		clientRecordAmountQual = ("Nothing", "Little", "Some", "A Lot")
		clientRecordPlanQual = ("No", "Maybe", "Yes")
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
		
		errs = []
		
		for csvRow in csvReader:
			
			try:
			
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
						replaceQualitativeWithQuantitativeByPosition(clientRecordVals, ("useful", "appropriate"), clientRecordAgreeQual)
						replaceQualitativeWithQuantitativeByPosition(clientRecordVals, ("learned",), clientRecordAmountQual)
						replaceQualitativeWithQuantitativeByPosition(clientRecordVals, ("again", "recommend"), clientRecordPlanQual)
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
				
			except Exception as error:
				errs.append(str(error))
		
		self.connection.commit()
		csvFile.close()
		
		if len(errs) > 0:
			return ("An error occured while adding data from CSV file '{}'.".format(os.path.basename(csvPath)), "\n".join(errs))
		
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
		
	def validateParamValues(self):
		errors = []
		for param in self.parameters:
			val = param.values
			if len(val) == 0 and param.required == True:
				errors.append("No value specified for required parameter '{}'".format(param.name))
			if param.paramType == "select":
				for thisVal in val:
					if not thisVal in param.options:
							errors.append("Invalid selection '{}' for parameter '{}'".format(thisVal, param.name))
			if param.paramType == "bool":
				for thisVal in val:
					if thisVal not in ["Yes", "No"]:
						errors.append("Invalid value '{}' for boolean parameter '{}'".format(thisVal, param.name))
		return errors
	
	# Rewrite queries to have the proper number of placeholders. Allows for selection of multiple values.
	def prepQuery(self):
		chunks = re.split("\?", self.query)
		newQuery = ""
		for i in range(len(chunks) - 1):
			val = self.parameters[i].values
			ph = "?"
			if isinstance(val, list):
				ph = ",".join("?"*len(val))
			newQuery += chunks[i] + ph
		newQuery += chunks[-1]
		return newQuery
	
	# Flatten parameter values so they can be fed to the SQLite module as one list
	def prepValues(self):
		nested = [param.values for param in self.parameters]
		flat = []
		for val in nested:
			if isinstance(val, list):
				flat.extend(val)
			else:
				flat.append(val)
		return flat

	@classmethod
	# Returns a SavedQuery if successful or an error tuple if not
	def initFromJsonString(self, jsonString):
		try:
			# `loads` puts everything in unicode; hence various str() casts below
			parsedJson = json.loads(jsonString)
		except Exception as error:
			return  ("Failed to load saved query: error parsing JSON.", str(error))
		name = str(parsedJson.get("name", ""))
		description = str(parsedJson.get("description", ""))
		query = str(parsedJson.get("query", ""))
		unicodeParams = parsedJson.get("parameters", [])
		params = []
		for thisParam in unicodeParams:
			paramObj = SavedQuery.Parameter.initFromJsonDict(thisParam)
			params.append(paramObj)
		if name == "" or query == "":
			return ("Failed to load saved query '{}': 'name' and 'query' parameters are required.".format(name),)
		if len(params) != query.count("?"):
			return("Failed to load saved query '{}': number of parameters ({}) must match number of placeholders in query string ({}).".format(name, len(params), query.count("?")),)
		return SavedQuery(name=name, description=description, query=query, parameters=params)
		
	@staticmethod
	# Returns a tuple where the first element is a list of successfully loaded queries,
	# and the second element is a list of errors.
	def loadAllForDataset(dataset):
		basePath = makePath("app/saved-queries/") + dataset + "/"
		filesList = listdir(basePath)
		parsedQueries = []
		errors = []
		for thisFile in filesList:
			if thisFile.endswith(".json"):
				openFile = open(basePath + thisFile, "r")
				jsonString = openFile.read()
				openFile.close()
				thisQuery = SavedQuery.initFromJsonString(jsonString)
				# Make sure the query was parsed successfully and is different from others in the list
				if isinstance(thisQuery, SavedQuery):
					identicalQueries = [query for query in parsedQueries if int(query.hash) == int(thisQuery.hash)]
					if len(identicalQueries) < 1:
						parsedQueries.append(thisQuery)
					else:
						errors.append(("Error loading saved query '{}': identical query already loaded under name '{}'".format(thisQuery.name, identicalQueries[0].name),))
				elif isinstance(thisQuery, tuple):
					errors.append(thisQuery)
		parsedQueries = sorted(parsedQueries, key=lambda k: k.name) # Alphabetize the list
		return (parsedQueries, errors)
		
	class Parameter(object):
		"""A parameter for a prepared database query"""
		
		def __init__(self, name = "", paramType = "", options = [], required = False, allowMulti = True, values = []):
			self.name = name
			self.paramType = paramType
			self.options = options
			self.required = required if required else False # Turn None into False
			self.allowMulti = True if allowMulti or allowMulti == None else False # Turn None into True
			self.values = values
		
		# Value declared as property so that setter can do some cleanup
		@property
		def values(self):
			return self._values
		@values.setter
		def values(self, val):
			# If multiple selections are allowed and any values are strings with multiple comma-separated items, split them up
			newVals = []
			for thisVal in val:
				if isinstance(thisVal, str):
					if self.allowMulti:
						thisVal = re.split(",\s*", thisVal)
					else:
						thisVal = [thisVal]
				newVals.extend(thisVal)
			self._values = newVals
		
		def __str__(self):
			return "Parameter '{}' ({}, type '{}')".format(self.name, "required" if self.required else "optional", self.paramType)
		
		@classmethod	
		def initFromJsonDict(self, jsonDict):
			# Convert unicode stuff into normal strings
			paramDetails = {}
			for key, val in jsonDict.iteritems():
				strKey = str(key)
				strVal = ""
				if isinstance(val, list): # Deal with unicode options arrays
					strVal = [str(thisVal) for thisVal in val]
				elif isinstance(val, bool): # Keep bool vals as bool, not str
					strVal = val
				else:
					strVal = str(val)
				paramDetails[strKey] = strVal
			# Build the parameter object
			paramObj = SavedQuery.Parameter(paramDetails.get("name"), paramDetails.get("type"), paramDetails.get("options"), paramDetails.get("required"), paramDetails.get("allowMulti"))
			return paramObj

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
		startupError = ("An error occurred creating the Sessions database.", error)
		
if not "eno.db" in dbFiles:
	try:
		openFile = open(makePath("app/db/eno-schema.sql"), "r")
		script = openFile.read()
		openFile.close()
		enoDb.executeScript(script)
	except Exception as error:
		startupError = ("An error occurred creating the Education & Outreach database.", error)

try:
	if not sessionsDb.validateOwnSchema():
		startupError = ("The Sessions database schema is invalid.",)
except Exception as error:
	startupError = ("An error occurred validating the Sessions database schema.", error)

try:
	if not enoDb.validateOwnSchema():
		startupError = ("The Education & Outreach database schema is invalid.",)
except Exception as error:
	startupError = ("An error occurred validating the Education & Outreach database schema.", error)

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

shutil.rmtree(makePath("app/download"))
os.mkdir(makePath("app/download"))
