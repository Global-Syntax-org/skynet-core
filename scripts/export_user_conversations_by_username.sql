-- Export user conversations by username (joins `users` -> `user_conversations`)
-- Usage (replace 'alice' below with the desired username):
--   sqlite3 -header -csv users.db "SELECT uc.id AS message_id, u.id AS user_id, u.username, uc.message_type AS role, uc.content AS message, uc.timestamp FROM user_conversations uc JOIN users u ON u.id = uc.user_id WHERE u.username = 'alice' ORDER BY uc.timestamp ASC;" > alice_conversations.csv

SELECT
  uc.id AS message_id,
  u.id AS user_id,
  u.username,
  uc.message_type AS role,
  uc.content AS message,
  uc.timestamp
FROM user_conversations uc
JOIN users u ON u.id = uc.user_id
WHERE u.username = 'alice'
ORDER BY uc.timestamp ASC;
-- Export user conversations by username (joins `users` -> `user_conversations`)
-- Usage (replace 'alice' below with the desired username):
--   sqlite3 -header -csv users.db "SELECT uc.id AS message_id, u.id AS user_id, u.username, uc.message_type AS role, uc.content AS message, uc.timestamp FROM user_conversations uc JOIN users u ON u.id = uc.user_id WHERE u.username = 'alice' ORDER BY uc.timestamp ASC;" > alice_conversations.csv

SELECT
  uc.id AS message_id,
  u.id AS user_id,
  u.username,
  uc.message_type AS role,
  uc.content AS message,
  uc.timestamp
FROM user_conversations uc
JOIN users u ON u.id = uc.user_id
WHERE u.username = 'alice'
ORDER BY uc.timestamp ASC;
