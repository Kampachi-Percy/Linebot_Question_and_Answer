.mode csv
CREATE TABLE tmp(genre, question, answer);
.import questions.csv tmp
INSERT INTO questions(genre, question, answer) SELECT * FROM tmp;
DROP TABLE tmp;