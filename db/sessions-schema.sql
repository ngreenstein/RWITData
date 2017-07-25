CREATE TABLE "centerSessions" (
	"id" INTEGER PRIMARY KEY NOT NULL UNIQUE,
	"clientId" INTEGER REFERENCES "people.id"(""),
	"tutorId" INTEGER REFERENCES "people.id"(""),
	"type" TEXT,
	"term" TEXT,
	"startTime" INTEGER,
	"stopTime" INTEGER,
	"creationTime" INTEGER,
	"updateTime" INTEGER,
	"state" TEXT,
	"tutorRecordId" INTEGER REFERENCES "tutorRecords.id"(""),
	"clientRecordId" INTEGER REFERENCES "clientRecords.id"("")
);

CREATE TABLE "writingAssistantSessions" (
	"id" INTEGER PRIMARY KEY UNIQUE NOT NULL,
	"type" TEXT,
	"term" TEXT,
	"clientId" INTEGER REFERENCES "people.id"(""),
	"tutorId" INTEGER REFERENCES "people.id"(""),
	"date" INTEGER,
	"creationTime" INTEGER,
	"updateTime" INTEGER,
	"hours" REAL,
	"attendees" TEXT,
	"assignment" TEXT,
	"pagesAssigned" TEXT,
	"pagesReviewed" TEXT,
	"tutorFeedback" TEXT
);

CREATE TABLE "people" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
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
	"tutorId" INTEGER REFERENCES "people.id"(""),
	"centerSessionId" INTEGER REFERENCES "centerSessions.id"(""),
	"primaryDocumentType" TEXT,
	"otherPrimaryDocumentType" TEXT,
	"dueDate" INTEGER,
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
	"centerSessionId" INTEGER REFERENCES "centerSession.id"(""),
	"globalGoalsMet" TEXT,
	"localGoalsMet" TEXT,
	"feedback" TEXT,
	"suggestions" TEXT,
	"useful" TEXT,
	"appropriate" TEXT,
	"learned" TEXT,
	"again" TEXT,
	"recommend" TEXT
);