import sqlite3, os

db = 'gv_system/db.sqlite3'
if not os.path.exists(db):
    print('DB not found:', db)
    raise SystemExit(1)
conn = sqlite3.connect(db)
cur = conn.cursor()
try:
    cur.execute("SELECT id, reference_number, reporter_profile_id, reporter_email, reporter_name, created_at FROM reports_incidentreport ORDER BY created_at DESC LIMIT 100")
    rows = cur.fetchall()
    if not rows:
        print('No reports in DB')
    else:
        for r in rows:
            print(r)
finally:
    conn.close()
