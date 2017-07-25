CREATE TABLE "presentations" (
	"id" INTEGER UNIQUE NOT NULL PRIMARY KEY AUTOINCREMENT,
	"presentationType" TEXT,
	"date" INTEGER,
	"term" TEXT,
	"course" TEXT,
	"tutor1Name" TEXT,
	"tutor2Name" TEXT,
	"profName" TEXT,
	"classHour" TEXT,
	"xHour" INTEGER
);

CREATE TABLE "profRecords" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
	"presentationId" INTEGER REFERENCES "presentations.id"(""),
	"overallRating" REAL,
	"complementCourse" TEXT,
	"presentationInfo" TEXT,
	"presentationEffective" TEXT,
	"workshopEffective" TEXT,
	"likelihoodInvite" TEXT,
	"likelihoodRecommend" TEXT,
	"otherFeedback" TEXT
);

CREATE TABLE "studentRecords" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
	"presentationId" INTEGER REFERENCES "presentations.id"(""),
	"classYear" INTEGER,
	"overallRating" REAL,
	"presentationInfo" TEXT,
	"presentationEffective" TEXT,
	"workshopEffective" TEXT,
	"likelihoodVisit" TEXT,
	"likelihoodRecommend" TEXT,
	"otherFeedback" TEXT
);