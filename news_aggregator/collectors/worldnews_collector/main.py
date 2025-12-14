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

from news_aggregator.database import connection
import uuid

# Load dotenv logic is in main block or common lib, assumed loaded.

WORLDNEWS_KEY = os.getenv("WORLDNEWS_KEY")

BASE_URL = "https://api.worldnewsapi.com/search-news"

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
    
    # Placeholder logic
    placeholder = "?" if connection.get_db_type() == 'sqlite' else "%s"
    
    insert_sql = f"""
        INSERT INTO news_raw (id, source, title, description, url, published_at, content)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ON CONFLICT (url) DO NOTHING;
    """
    
    for a in items:
        title = a.get("title")
        desc = a.get("text") or a.get("description")
        link = a.get("url")
        published = parse_published(a.get("publish_date") or a.get("publishedAt") or a.get("published"))
        content = (a.get("text") or desc) or ""
        
        pk = str(uuid.uuid4())
        
        try:
            cur.execute(insert_sql, (pk, "worldnews", title, desc, link, published, content))
            print ("Inserido no Banco")
        except Exception as e:
            print("insert error", e)
    conn.commit()

if __name__ == "__main__":

    print("Starting WorldNews collector...")
    if not WORLDNEWS_KEY:
        raise SystemExit("Please set WORLDNEWS_KEY in environment")
    
    try:
        conn = connection.get_db_connection()
        while True:
            try:
                # collect_once prints results? removed duplicate print from original code
                collect_once(conn)
                print(f"[WorldNews] collecting at {datetime.utcnow().isoformat()}")
            except Exception as e:
                print("collector error", e)
            time.sleep(TIME_UPDATE)
    except Exception as e:
         print(f"Fatal error: {e}") 
