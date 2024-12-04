DROP TABLE IF EXISTS label;
DROP TABLE IF EXISTS meal;

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