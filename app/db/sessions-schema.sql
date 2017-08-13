CREATE TABLE "centerSessions" (
	"id" INTEGER PRIMARY KEY NOT NULL UNIQUE,
	"clientId" INTEGER REFERENCES "people.id"(""),
	"tutorId" INTEGER REFERENCES "tutorStubs.id"(""),
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
	/* WA sessions have real tutor data, so use `people` instead of `tutorStubs` */
	"tutorId" INTEGER REFERENCES "people.id"(""),
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
	"fluentWriting" TEXT,
	UNIQUE ("name", "deptClass")
);

/*
* Currently (17X), RWIT Online doesn't give any tutor info beyond name. Better info
* (and a better way to unique people in general) is theoretically coming soon, at which point
* tutors should be put into the `people` table with clients, and any `tutorId` column can
* reference `people(id)` instead of `tutorStubs(id)`.
*/
CREATE TABLE "tutorStubs" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
	"name" TEXT UNIQUE NOT NULL
);

CREATE TABLE "tutorRecords" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
	"tutorId" INTEGER REFERENCES "tutorStubs.id"(""),
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
	"clientId" INTEGER REFERENCES "people.id"(""),
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