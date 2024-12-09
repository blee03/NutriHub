DROP TABLE IF EXISTS label;
DROP TABLE IF EXISTS meal;
DROP TABLE IF EXISTS fruits;
DROP TABLE IF EXISTS vegetables;

CREATE TABLE label (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    fat INTEGER NOT NULL,
    protein INTEGER NOT NULL,
    carbs INTEGER NOT NULL
);

CREATE TABLE meal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servings INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(label_id) REFERENCES label(id)
);

CREATE TABLE IF NOT EXISTS vegetables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    fat INTEGER NOT NULL,
    carbs INTEGER NOT NULL,
    protein INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fruits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    fat INTEGER NOT NULL,
    carbs INTEGER NOT NULL,
    protein INTEGER NOT NULL
);

INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Broccoli', 55, 0, 11, 4);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Spinach', 23, 0, 4, 3);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Carrot', 41, 0, 10, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Tomato', 18, 0, 4, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Cucumber', 16, 0, 4, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Lettuce', 15, 0, 3, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Celery', 14, 0, 3, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Radish', 16, 0, 4, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Bell Pepper', 20, 0, 4, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Zucchini', 17, 0, 3, 1);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Cauliflower', 25, 0, 5, 2);
INSERT INTO vegetables (name, calories, fat, carbs, protein) VALUES ('Cabbage', 25, 0, 6, 1);


INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Apple', 52, 0, 14, 0);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Banana', 96, 0, 27, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Orange', 47, 0, 12, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Grapes', 69, 0, 18, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Watermelon', 30, 0, 8, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Strawberry', 32, 0, 8, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Mango', 60, 0, 15, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Blueberry', 57, 0, 14, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Pineapple', 50, 0, 13, 0);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Pear', 57, 0, 15, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Cherry', 50, 0, 12, 1);
INSERT INTO fruits (name, calories, fat, carbs, protein) VALUES ('Papaya', 43, 0, 11, 0);


