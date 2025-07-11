CREATE DATABASE IF NOT EXISTS flask_attendance;
USE flask_attendance;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    username VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
);

INSERT INTO users (name, username, email, password)
VALUES ('Admin User', 'admin', 'admin@example.com', 'admin123');

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    username VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    city VARCHAR(255),
    photo VARCHAR(255)
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date DATE,
    sign_in TIME,
    sign_out TIME
);
