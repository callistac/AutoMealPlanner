/* commands */
.mode column
.header ON

/* DROP TABLE user_info;
DROP TABLE allergies;  Drops tables completely */

DROP TABLE user_info;
CREATE TABLE user_info
  (username VARCHAR(30) NOT NULL,
  password VARCHAR(255) NOT NULL,
  zipcode integer,
  weekly_budget integer,
  PRIMARY KEY (username)
  );

/* Deletes table contents */
DELETE FROM allergies;

INSERT INTO user_info(username, password, zipcode, weekly_budget)
VALUES ("testing", "pass123", 60637, 100);

INSERT INTO user_info(username, password, zipcode, weekly_budget)
VALUES ("callistac", "pass1234", 60637, 100);

INSERT INTO user_info(username, password, zipcode, weekly_budget)
VALUES ("kgozman", "ilovemarty", 60637, 10000);

INSERT INTO allergies(username, allergy)
VALUES ("kgozman", "vegan");

SELECT * FROM user_info;
SELECT * FROM allergies;
SELECT u.username, u.zipcode, u.weekly_budget, a.allergy FROM user_info AS u JOIN allergies AS a ON u.username = a.username;
