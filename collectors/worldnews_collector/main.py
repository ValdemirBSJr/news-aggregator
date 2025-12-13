"""
World News API collector: fetch news filtered by country and insert into news_raw.
API docs: https://worldnewsapi.com/
Run periodically.
"""
import os
import time
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WORLDNEWS_KEY = os.getenv("WORLDNEWS_KEY")
DB_DSN = (
    f"host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT',5432)} "
    f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}"
)

BASE_URL = "https://api.worldnewsapi.com/search-news"
INSERT_SQL = """
    INSERT INTO news_raw (source, title, description, url, published_at, content)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO NOTHING;
"""


TIME_UPDATE = int(os.getenv('INTERVAL_UPDATE', 10800))

def fetch_worldnews(country="br", number=10):
    params = {
        "api-key": WORLDNEWS_KEY,
        "source-countries": country,
        "number": number,
        "language": "pt"
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    # docs may vary; the scaffold earlier used key 'news'
    # try both common shapes:
    return data.get("news") or data.get("articles") or []

def parse_published(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

def collect_once(conn):
    items = fetch_worldnews()
    cur = conn.cursor()
    for a in items:
        title = a.get("title")
        desc = a.get("text") or a.get("description")
        link = a.get("url")
        published = parse_published(a.get("publish_date") or a.get("publishedAt") or a.get("published"))
        content = (a.get("text") or desc) or ""
        try:
            cur.execute(INSERT_SQL, ("worldnews", title, desc, link, published, content))
            print ("Inserido no Banco")
        except Exception as e:
            print("insert error", e)
    conn.commit()

if __name__ == "__main__":

    print("Starting WorldNews collector...")
    if not WORLDNEWS_KEY:
        raise SystemExit("Please set WORLDNEWS_KEY in environment")
    
    with psycopg2.connect(DB_DSN) as conn:
        while True:
            try:
                collect_once(conn)
                print(f"[WorldNews] collecting at {datetime.utcnow().isoformat()}")
                print (collect_once(conn))
            except Exception as e:
                print("collector error", e)
            time.sleep(TIME_UPDATE) 
