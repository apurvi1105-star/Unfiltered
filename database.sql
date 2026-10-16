CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(20),
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS diary_entry (
    username VARCHAR(50) NOT NULL,
    diary_entry LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emotions(
    emotion_id INT AUTO_INCREMENT PRIMARY KEY,
    diary_id INT NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,

    FOREIGN KEY (diary_id)
    REFERENCES diary_entry(diary_id)
    ON DELETE CASCADE
);