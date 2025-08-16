#!/usr/bin/env bash
set -euo pipefail
# Creates sample DB, runs export script, prints output CSVs
DB=test_users.db
rm -f "$DB" user_1.csv bob.csv

# Create DB from SQL using sqlite3 CLI when available, otherwise fall back to Python
if command -v sqlite3 >/dev/null 2>&1; then
	sqlite3 "$DB" < scripts/test_create_sample_db.sql
else
	echo "sqlite3 CLI not found; using python's sqlite3 module as fallback"
	# Use an unindented closing marker so the shell recognizes it reliably.
	python3 - <<PY
import sqlite3, sys
db = "${DB}"
sql = open('scripts/test_create_sample_db.sql', 'r', encoding='utf-8').read()
conn = sqlite3.connect(db)
conn.executescript(sql)
conn.close()
print('Created', db)
PY
fi

python3 scripts/export_conversations.py --db "$DB" --userid 1 --out user_1.csv
python3 scripts/export_conversations.py --db "$DB" --username bob --out bob.csv

echo '=== user_1.csv ==='
cat user_1.csv || true

echo '=== bob.csv ==='
cat bob.csv || true
