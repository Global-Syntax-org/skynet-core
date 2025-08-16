-- Export user conversations from the `user_conversations` table (created by `web/auth.py`)
-- Usage (replace USER_ID with the numeric id):
--   sqlite3 -header -csv users.db "SELECT id AS message_id, user_id, message_type AS role, content AS message, timestamp FROM user_conversations WHERE user_id = 42 ORDER BY timestamp ASC;" > user_conversations_42.csv
--
-- Example (using the SQL file directly; edit the 42 below or use your own wrapper script):
--   sqlite3 -header -csv users.db < scripts/export_user_conversations_by_userid.sql > user_conversations_42.csv

SELECT
  id AS message_id,
  user_id,
  message_type AS role,
  content AS message,
  timestamp
FROM user_conversations
WHERE user_id = 42
ORDER BY timestamp ASC;
-- Export user conversations from the `user_conversations` table (created by `web/auth.py`)
-- Usage (replace USER_ID with the numeric id):
--   sqlite3 -header -csv users.db "SELECT id AS message_id, user_id, message_type AS role, content AS message, timestamp FROM user_conversations WHERE user_id = 42 ORDER BY timestamp ASC;" > user_conversations_42.csv
--
-- Example (using the SQL file directly; edit the 42 below or use your own wrapper script):
--   sqlite3 -header -csv users.db < scripts/export_user_conversations_by_userid.sql > user_conversations_42.csv

SELECT
  id AS message_id,
  user_id,
  message_type AS role,
  content AS message,
  timestamp
FROM user_conversations
WHERE user_id = 42
ORDER BY timestamp ASC;
