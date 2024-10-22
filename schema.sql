CREATE TABLE IF NOT EXISTS users (
user_id SERIAL PRIMARY KEY,
email VARCHAR(255) NOT NULL UNIQUE,
username VARCHAR(255) NOT NULL UNIQUE,
password VARCHAR(255)
);

-- CREATE TABLE IF NOT EXISTS food (

-- );

-- CREATE TABLE IF NOT EXISTS meal (

-- );


-- Test Data Only, Do Not Add to Your Real Database

INSERT INTO users (email, username, password)
VALUES
    ('johndoe@example.com', 'johndoe', 'password1'),
    ('bobross@example.com', 'bobross', 'password2'),
    ('lebronjames@example.com', 'lebronjames', 'password3'),
    ('sydsarah@example.com', 'sydsarah', 'password4');