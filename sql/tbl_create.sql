-- drop table if exists Album;
CREATE TABLE Album(
	albumid INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	title VARCHAR(50),
	created DATETIME,
	lastupdated DATETIME,
	permission VARCHAR(7)
);

create Table Photo(
	sequencenum INT NOT NULL,
	url VARCHAR(255),
	filename VARCHAR(7),
	caption VARCHAR(255),
	datetaken DATETIME
)
