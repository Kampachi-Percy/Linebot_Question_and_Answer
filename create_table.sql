CREATE TABLE users(
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    status TEXT DEFAULT "free",
    question_genre TEXT DEFAULT "未選択",
    question_number INTEGER DEFAULT 0,
    otetsuki_counter INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions(
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre TEXT,
    question TEXT,
    answer TEXT,
    author TEXT,
    correct_count INTEGER,
    asked_count INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER when_user_updated AFTER UPDATE ON users
BEGIN
UPDATE users SET updated_at = datetime('now', 'localtime') WHERE user_id = OLD.user_id;
END;

CREATE TRIGGER when_question_updated AFTER UPDATE ON questions
BEGIN
UPDATE questions SET updated_at = datetime('now', 'localtime') WHERE question_id = OLD.question_id;
END;