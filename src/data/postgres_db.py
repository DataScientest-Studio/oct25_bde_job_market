import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
PG_CONN = os.getenv("PG_CONN")

def get_latest_job_date_sql():
    """
    Returns the newest job 'created' timestamp in the database.
    Returns None if table does not exist or DB is empty.
    """
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(created) FROM Job;")
        latest = cur.fetchone()[0]
    except psycopg2.errors.UndefinedTable:
        conn.rollback()
        latest = None

    cur.close()
    conn.close()
    return latest

def store_jobs_sql(jobs):
    """
    Store a list of job dictionaries in PostgreSQL.
    Only inserts new jobs; duplicates are skipped.
    Returns the number of NEW jobs inserted.
    """
    if not jobs:
        print("No jobs to insert.")
        return 0
    
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()

    # ================================
    # CREATE TABLES
    # ================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Company (
        company_id SERIAL PRIMARY KEY,
        company_name TEXT UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Category (
        category_id SERIAL PRIMARY KEY,
        tag TEXT UNIQUE,
        label TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Location (
        location_id SERIAL PRIMARY KEY,
        display_name TEXT UNIQUE,
        latitude NUMERIC,
        longitude NUMERIC,
        country TEXT,
        city TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Job (
        job_id BIGINT PRIMARY KEY,
        title TEXT,
        contract_type TEXT,
        contract_time TEXT,
        created TIMESTAMP,
        adref TEXT,
        redirect_url TEXT,
        salary_min INT,
        salary_max INT,
        company_id INT REFERENCES Company(company_id),
        location_id INT REFERENCES Location(location_id),
        category_id INT REFERENCES Category(category_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS JobDescription (
        job_id BIGINT PRIMARY KEY REFERENCES Job(job_id),
        description_text TEXT
    );
    """)

    # ================================
    # INSERT DATA
    # ================================
    inserted_count = 0

    for job in jobs:
        # -----------------------------------
        # 1. Company
        # -----------------------------------
        company_name = job.get("company", {}).get("display_name")

        cur.execute("""
            INSERT INTO Company (company_name)
            VALUES (%s)
            ON CONFLICT (company_name) DO UPDATE SET company_name = EXCLUDED.company_name
            RETURNING company_id;
        """, (company_name,))
        company_id = cur.fetchone()[0]

        # -----------------------------------
        # 2. Category
        # -----------------------------------
        cat = job.get("category", {})
        tag = cat.get("tag")
        label = cat.get("label")

        cur.execute("""
            INSERT INTO Category (tag, label)
            VALUES (%s, %s)
            ON CONFLICT (tag) DO UPDATE SET label = EXCLUDED.label
            RETURNING category_id;
        """, (tag, label))
        category_id = cur.fetchone()[0]

        # -----------------------------------
        # 3. Location
        # Extract city + country from area list
        # -----------------------------------
        loc = job.get("location", {})
        display_name = loc.get("display_name")
        latitude = job.get("latitude")
        longitude = job.get("longitude")
        area_list = loc.get("area", [])

        country = area_list[0] if len(area_list) > 0 else None
        city = area_list[-2] if len(area_list) >= 2 else None   # usually second last

        cur.execute("""
            INSERT INTO Location (display_name, latitude, longitude, country, city)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (display_name)
               DO UPDATE SET latitude = EXCLUDED.latitude
            RETURNING location_id;
        """, (display_name, latitude, longitude, country, city))
        location_id = cur.fetchone()[0]

        # -----------------------------------
        # 4. Job
        # -----------------------------------
        cur.execute("""
            INSERT INTO Job (
                job_id, title, contract_type, contract_time, created,
                adref, redirect_url, salary_min, salary_max,
                company_id, location_id, category_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id) DO NOTHING
            RETURNING job_id;
        """, (
            job.get("id"),
            job.get("title"),
            job.get("contract_type"),
            job.get("contract_time"),
            job.get("created"),
            job.get("adref"),
            job.get("redirect_url"),
            job.get("salary_min"),
            job.get("salary_max"),
            company_id,
            location_id,
            category_id
        ))

        if cur.fetchone():
            inserted_count += 1

    print(f"✅ Inserted {inserted_count} new jobs into SQL database.\n")

    conn.commit()
    cur.close()
    conn.close()

    return inserted_count