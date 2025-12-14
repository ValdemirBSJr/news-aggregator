"""
NewsAPI collector: fetch top headlines for Brazil and insert into news_raw.
Run periodically (cron/container loop).
"""
import os
import time
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
DB_DSN = (
    f"host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT',5432)} "
    f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}"
)

BASE_URL = "https://newsapi.org/v2/top-headlines"
INSERT_SQL = """
    INSERT INTO news_raw (source, title, description, url, published_at, content)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO NOTHING;
"""

TIME_UPDATE = int(os.getenv('INTERVAL_UPDATE', 10800))

def fetch_newsapi(country="us", page_size=10):
    params = {
        "apiKey": NEWSAPI_KEY,
        "country": country,
        "pageSize": page_size
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data.get("articles", [])

def parse_published(published_at):
    if not published_at:
        return None
    try:
        # e.g. 2025-12-11T12:34:56Z
        return datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except Exception:
        return None

def collect_once(conn):
    articles = fetch_newsapi()
    cur = conn.cursor()
    for a in articles:
        title = a.get("title")
        desc = a.get("description")
        link = a.get("url")
        published = parse_published(a.get("publishedAt"))
        content = a.get("content") or desc or ""
        try:
            print (a)
            cur.execute(INSERT_SQL, ("newsapi", title, desc, link, published, content))
        except Exception as e:
            print("insert error", e)
    conn.commit()

if __name__ == "__main__":

    if not NEWSAPI_KEY:
        raise SystemExit("Please set NEWSAPI_KEY in environment")
    with psycopg2.connect(DB_DSN) as conn:
        while True:
            try:
                print(f"[NewsAPI] collecting at {datetime.utcnow().isoformat()}")
                collect_once(conn)
            except Exception as e:
                print("collector error", e)
            time.sleep(TIME_UPDATE) 