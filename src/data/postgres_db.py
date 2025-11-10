import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
PG_CONN = os.getenv("PG_CONN")

def store_jobs_sql(jobs):
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        created DATE,
        description TEXT
    )
    """)

    for job in jobs:
        cur.execute("""
            INSERT INTO jobs (title, company, location, created, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            job.get("title"),
            job.get("company", {}).get("display_name"),
            job.get("location", {}).get("display_name"),
            job.get("created"),
            job.get("description")
        ))

    conn.commit()
    cur.close()
    conn.close()
