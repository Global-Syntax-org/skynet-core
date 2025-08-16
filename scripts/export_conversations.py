#!/usr/bin/env python3
"""Export user conversations to CSV.

Usage:
  ./scripts/export_conversations.py --db users.db --userid 42 --out user_42.csv
  ./scripts/export_conversations.py --db users.db --username alice --out alice.csv

If both --userid and --username are provided, --userid takes precedence.
"""
import argparse
import csv
import sqlite3
from typing import Optional


def export_by_userid(db_path: str, user_id: int, out_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """SELECT uc.id AS message_id, uc.user_id, uc.message_type AS role, uc.content AS message, uc.timestamp
           FROM user_conversations uc
           WHERE uc.user_id = ?
           ORDER BY uc.timestamp ASC;""",
        (user_id,)
    )
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()


def export_by_username(db_path: str, username: str, out_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """SELECT uc.id AS message_id, u.id AS user_id, u.username, uc.message_type AS role, uc.content AS message, uc.timestamp
           FROM user_conversations uc
           JOIN users u ON u.id = uc.user_id
           WHERE u.username = ?
           ORDER BY uc.timestamp ASC;""",
        (username,)
    )
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()


def main():
    p = argparse.ArgumentParser(description="Export user conversations to CSV")
    p.add_argument("--db", default="users.db", help="Path to sqlite DB (default: users.db)")
    p.add_argument("--userid", type=int, help="Numeric user id to export")
    p.add_argument("--username", help="Username to export")
    p.add_argument("--out", required=True, help="Output CSV path")

    args = p.parse_args()

    if args.userid:
        export_by_userid(args.db, args.userid, args.out)
        print(f"Exported conversations for user_id={args.userid} to {args.out}")
    elif args.username:
        export_by_username(args.db, args.username, args.out)
        print(f"Exported conversations for username='{args.username}' to {args.out}")
    else:
        p.error("Either --userid or --username must be provided")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Export user conversations to CSV.

Usage:
  ./scripts/export_conversations.py --db users.db --userid 42 --out user_42.csv
  ./scripts/export_conversations.py --db users.db --username alice --out alice.csv

If both --userid and --username are provided, --userid takes precedence.
"""
import argparse
import csv
import sqlite3
from typing import Optional


def export_by_userid(db_path: str, user_id: int, out_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """SELECT uc.id AS message_id, uc.user_id, uc.message_type AS role, uc.content AS message, uc.timestamp
           FROM user_conversations uc
           WHERE uc.user_id = ?
           ORDER BY uc.timestamp ASC;""",
        (user_id,)
    )
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()


def export_by_username(db_path: str, username: str, out_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """SELECT uc.id AS message_id, u.id AS user_id, u.username, uc.message_type AS role, uc.content AS message, uc.timestamp
           FROM user_conversations uc
           JOIN users u ON u.id = uc.user_id
           WHERE u.username = ?
           ORDER BY uc.timestamp ASC;""",
        (username,)
    )
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()


def main():
    p = argparse.ArgumentParser(description="Export user conversations to CSV")
    p.add_argument("--db", default="users.db", help="Path to sqlite DB (default: users.db)")
    p.add_argument("--userid", type=int, help="Numeric user id to export")
    p.add_argument("--username", help="Username to export")
    p.add_argument("--out", required=True, help="Output CSV path")

    args = p.parse_args()

    if args.userid:
        export_by_userid(args.db, args.userid, args.out)
        print(f"Exported conversations for user_id={args.userid} to {args.out}")
    elif args.username:
        export_by_username(args.db, args.username, args.out)
        print(f"Exported conversations for username='{args.username}' to {args.out}")
    else:
        p.error("Either --userid or --username must be provided")


if __name__ == "__main__":
    main()
