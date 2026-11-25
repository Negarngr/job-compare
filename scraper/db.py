import sqlite3, json, os, datetime as dt


def conn():
    os.makedirs("data", exist_ok=True)
    c = sqlite3.connect("data/jobs.db")
    c.execute("""CREATE TABLE IF NOT EXISTS jobs(
        url TEXT PRIMARY KEY, source TEXT, company TEXT, country TEXT, title TEXT,
        skills TEXT, responsibilities TEXT, first_seen TEXT, last_seen TEXT, active INTEGER)""")
    return c


def upsert(jobs):
    if not jobs:
        return
    c, today = conn(), dt.date.today().isoformat()
    sources = sorted({j["source"] for j in jobs})
    c.execute(f"UPDATE jobs SET active=0 WHERE source IN ({','.join('?' * len(sources))})", sources)
    for j in jobs:
        sk = json.dumps(j["skills"])
        rs = json.dumps(j["responsibilities"], ensure_ascii=False)
        c.execute("""INSERT INTO jobs(url,source,company,country,title,skills,responsibilities,first_seen,last_seen,active)
            VALUES(?,?,?,?,?,?,?,?,?,1)
            ON CONFLICT(url) DO UPDATE SET last_seen=?, active=1, skills=?, responsibilities=?, title=?""",
                  (j["url"], j["source"], j["company"], j["country"], j["title"], sk, rs, today, today,
                   today, sk, rs, j["title"]))
    c.commit()
    c.close()
