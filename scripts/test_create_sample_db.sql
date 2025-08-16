-- Creates a small sample SQLite DB compatible with the project's schema
-- Usage:
--   sqlite3 test_users.db < scripts/test_create_sample_db.sql

DROP TABLE IF EXISTS user_conversations;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE user_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

INSERT INTO users (username, password_hash, email) VALUES ('alice','x','alice@example.com');
INSERT INTO users (username, password_hash, email) VALUES ('bob','x','bob@example.com');

INSERT INTO user_conversations (user_id, message_type, content, timestamp) VALUES (1,'user','Hello from Alice','2025-08-16 10:00:00');
INSERT INTO user_conversations (user_id, message_type, content, timestamp) VALUES (1,'assistant','Hi Alice','2025-08-16 10:00:01');
INSERT INTO user_conversations (user_id, message_type, content, timestamp) VALUES (2,'user','Bob here','2025-08-16 11:00:00');
