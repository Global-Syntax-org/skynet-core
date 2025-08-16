Exporting conversation history

This folder contains small SQL helpers to export conversation history from the project's SQLite database (by default `users.db` in the repo root).

Files:
- `export_user_conversations_by_userid.sql` - template SQL to export all messages for a numeric `user_id`.
- `export_user_conversations_by_username.sql` - template SQL that joins `users` and `user_conversations` and exports messages for a given username.

Usage examples:

Export by user id (replace 42 with user id):

```bash
sqlite3 -header -csv users.db "SELECT id AS message_id, user_id, message_type AS role, content AS message, timestamp FROM user_conversations WHERE user_id = 42 ORDER BY timestamp ASC;" > user_conversations_42.csv
```

Or edit `scripts/export_user_conversations_by_userid.sql` and change the `WHERE user_id = 42` line, then:

```bash
sqlite3 -header -csv users.db < scripts/export_user_conversations_by_userid.sql > user_conversations_42.csv
```

Export by username (replace alice with username):

```bash
sqlite3 -header -csv users.db "SELECT uc.id AS message_id, u.id AS user_id, u.username, uc.message_type AS role, uc.content AS message, uc.timestamp FROM user_conversations uc JOIN users u ON u.id = uc.user_id WHERE u.username = 'alice' ORDER BY uc.timestamp ASC;" > alice_conversations.csv
```

Notes:
- The project uses the `user_conversations` table (columns: id, user_id, message_type, content, timestamp) as defined in `web/auth.py`.
- `users.db` is the default path used by `AuthManager` unless you configured a different `db_path`.
- For automation, consider writing a small wrapper script that accepts a username or user id and invokes sqlite3 with the appropriate query.
