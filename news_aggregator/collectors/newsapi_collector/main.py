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

from news_aggregator.database import connection
import uuid

# Remove direct load_dotenv and os.getenv for DB here, handled by connection
# But NEWSAPI_KEY and INTERVAL still needed.

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
# DB_DSN removido

BASE_URL = "https://newsapi.org/v2/top-headlines"

# SQL Generico (placeholders serao ajustados)
# Postgres supporta ON CONFLICT (url) DO NOTHING
# SQLite suporte ON CONFLICT(url) DO NOTHING
# A sintaxe é compativel.
# Porem o placeholder é diferente.

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
    
    # Get SQL with correct placeholders
    # PG: %s, SQLite: ?
    placeholder = "?" if connection.get_db_type() == 'sqlite' else "%s"
    
    insert_sql = f"""
        INSERT INTO news_raw (id, source, title, description, url, published_at, content)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ON CONFLICT (url) DO NOTHING;
    """
    
    for a in articles:
        title = a.get("title")
        desc = a.get("description")
        link = a.get("url")
        published = parse_published(a.get("publishedAt"))
        content = a.get("content") or desc or ""
        
        # ID gen
        # Postgres has default uuid_generate_v4(). SQLite does not.
        # So we generate UUID in python if using SQLite, OR if using Postgres (to be safe/uniform)
        # Actually our PG schema has default. But if we provide it, it overrides.
        pk = str(uuid.uuid4())
        
        try:
            print (a)
            cur.execute(insert_sql, (pk, "newsapi", title, desc, link, published, content))
        except Exception as e:
            print("insert error", e)
    conn.commit()

if __name__ == "__main__":

    print (fetch_newsapi())
    if not NEWSAPI_KEY:
        raise SystemExit("Please set NEWSAPI_KEY in environment")
if __name__ == "__main__":

    print (fetch_newsapi())
    if not NEWSAPI_KEY:
        raise SystemExit("Please set NEWSAPI_KEY in environment")
    
    # Use our connection wrapper
    try:
        conn = connection.get_db_connection()
        while True:
            try:
                print(f"[NewsAPI] collecting at {datetime.utcnow().isoformat()}")
                collect_once(conn)
            except Exception as e:
                print("collector error", e)
                # Re-connect if connection lost?
                # For simplicity, if fatal error, maybe we crash or retry connection. 
                # connection.get_db_connection returns new conn if needed but here we hold it.
            time.sleep(TIME_UPDATE)
    except Exception as e:
        print(f"Fatal error: {e}") 