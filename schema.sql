CREATE DATABASE book_recommendation;

-- Use the database
USE book_recommendation;

-- Create books table
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    author VARCHAR(255),
    image_url TEXT
);

-- Create user ratings table
CREATE TABLE user_ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    user_rating FLOAT CHECK (user_rating BETWEEN 1 AND 5),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);