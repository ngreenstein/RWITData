CREATE TABLE "centerSessions" (
	"id" INTEGER PRIMARY KEY NOT NULL UNIQUE,
	"clientId" TEXT REFERENCES "people.netId"(""),
	"tutorId" TEXT REFERENCES "people.netId"(""),
	"type" TEXT,
	"term" TEXT,
	"startTime" TEXT,
	"stopTime" TEXT,
	"creationTime" TEXT,
	"updateTime" TEXT,
	"state" TEXT,
	"tutorRecordId" INTEGER REFERENCES "tutorRecords.id"(""),
	"clientRecordId" INTEGER REFERENCES "clientRecords.id"("")
);

CREATE TABLE "writingAssistantSessions" (
	"id" INTEGER PRIMARY KEY UNIQUE NOT NULL,
	"tutorId" TEXT REFERENCES "people.netId"(""),
	"type" TEXT,
	"term" TEXT,
	"date" TEXT,
	"creationTime" TEXT,
	"updateTime" TEXT,
	"hours" REAL,
	"attendees" TEXT,
	"assignment" TEXT,
	"pagesAssigned" TEXT,
	"pagesReviewed" TEXT,
	"tutorFeedback" TEXT
);

CREATE TABLE "people" (
	"netId" TEXT PRIMARY KEY UNIQUE NOT NULL,
	"name" TEXT,
	"status" TEXT,
	"deptClass" TEXT,
	"majors" TEXT,
	"minors" TEXT,
	"otherMajorMinor" TEXT,
	"modifieds" TEXT,
	"graduatePrograms" TEXT,
	"firstLanguage" TEXT,
	"fluentSpeaking" TEXT,
	"fluentReading" TEXT,
	"fluentWriting" TEXT
);

CREATE TABLE "tutorRecords" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
	"tutorId" TEXT REFERENCES "people.netId"(""),
	"primaryDocumentType" TEXT,
	"otherPrimaryDocumentType" TEXT,
	"dueDate" TEXT,
	"documentTypes" TEXT,
	"documentCategories" TEXT,
	"documentLanguages" TEXT,
	"writingPhases" TEXT,
	"globalGoals" TEXT,
	"globalGoalsMet" TEXT,
	"localGoals" TEXT,
	"localGoalsMet" TEXT,
	"outcomes" TEXT,
	"strategies" TEXT,
	"tutorFeedback" TEXT,
	"tutorSelfAssess" TEXT
);

CREATE TABLE "clientRecords" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
	"clientId" TEXT REFERENCES "people.netId"(""),
	"globalGoalsMet" TEXT,
	"localGoalsMet" TEXT,
	"feedback" TEXT,
	"suggestions" TEXT,
	"useful" INTEGER,
	"appropriate" INTEGER,
	"learned" INTEGER,
	"again" INTEGER,
	"recommend" INTEGER
);