/* use this to instantiate user_info table */
CREATE TABLE user_info
  (username VARCHAR(30) NOT NULL,
  password VARCHAR(30) NOT NULL,
  zipcode integer,
  weekly_budget integer,
  PRIMARY KEY (username)
  );

/* A FOREIGN KEY is a field (or collection of fields) in one table that refers to the PRIMARY KEY in another table.
allergy table */
CREATE TABLE allergies
  (username VARCHAR(30) NOT NULL,
  allergy VARCHAR(30),
  FOREIGN KEY (username) REFERENCES user_info(username)
  );

/* use this to instantiate recipes table */
CREATE TABLE recipes
  (id integer NOT NULL,
   url VARCHAR(100) NOT NULL,
   recipe_name VARCHAR(15),
   PRIMARY KEY (id)
  );

CREATE TABLE ingredients
  (id integer NOT NULL,
  ingredient VARCHAR(100),
  FOREIGN KEY (id) REFERENCES recipes(id)
);

CREATE TABLE cusine
  (id integer NOT NULL,
  cuisine VARCHAR(30),
  FOREIGN KEY (id) REFERENCES recipes(id)
);
