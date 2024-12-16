DROP DATABASE IF EXISTS TaskReminder;
CREATE DATABASE IF NOT exists TaskReminder;

USE TaskReminder;

CREATE TABLE Users
(
	user_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Tasks
(
	task_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    priority ENUM('High', 'Medium', 'Low') DEFAULT 'Low',
    status ENUM('Pending', 'Completed', 'Overdue') DEFAULT 'Pending',
    due_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Reminders
(
	reminder_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL UNIQUE,
    reminder_time DATETIME NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE
);

CREATE TABLE Settings (
    setting_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    notification_enabled BOOLEAN DEFAULT TRUE,
    theme ENUM('Light', 'Dark') DEFAULT 'Light',
    timezone VARCHAR(50) DEFAULT 'UTC',
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
