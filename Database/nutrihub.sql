CREATE TABLE label (
    id INT NOT NULL AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    calories INT NULL,
    total_fat DECIMAL(5,2) NULL,
    cholesterol DECIMAL(5,2) NULL,
    sodium DECIMAL(5,2) NULL,
    carbohydrates DECIMAL(5,2) NULL,
    protein DECIMAL(5,2) NULL,
    PRIMARY KEY (id, filename)
);

CREATE TABLE meal (
    id INT NOT NULL AUTO_INCREMENT,
    servings INT NULL,
    meal_date DATE NULL,
    meal_time TIME NULL,
    label_id INT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE goals (
    user_id INT NOT NULL,
    current_goal VARCHAR(255) NULL,
    macro_goals VARCHAR(255) NULL,
    fat DECIMAL(5,2) NULL,
    cholesterol DECIMAL(5,2) NULL,
    sodium DECIMAL(5,2) NULL,
    carbohydrates DECIMAL(5,2) NULL,
    protein DECIMAL(5,2) NULL,
    PRIMARY KEY (user_id)
);