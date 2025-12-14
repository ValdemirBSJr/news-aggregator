"""
World News API collector: pega as notícias do World News API e insere no news_raw.
API docs: https://worldnewsapi.com/
Roda periodicamente (cron loop).
"""
import os
import time
import requests
from datetime import datetime
from news_aggregator.database import connection
import uuid
from dotenv import load_dotenv

load_dotenv()


# Vamos carregar as chaves de api das noticias
WORLDNEWS_KEY = os.getenv("WORLDNEWS_API_KEY") or os.getenv("WORLDNEWS_KEY")

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
    
    # Logica do placeholder sqlite
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
            print("Erro ao inserir no banco: ", e)
    conn.commit()

def run_collector_loop():
    print("[INFO] Iniciando loop do coletor WorldNews...")
    if not WORLDNEWS_KEY:
        print("[ERROR] Chave do WorldNews não configurada, pulando o coletor.")
        return
    
    try:
        conn = connection.get_db_connection()
        while True:
            try:
                collect_once(conn)
                print(f"[INFO] WorldNews coletando em: {datetime.utcnow().isoformat()}")
            except Exception as e:
                print("[ERROR] Erro do coletor: ", e)
            time.sleep(TIME_UPDATE)
    except Exception as e:
         print(f"[ERROR] Erro fatal: {e}")

if __name__ == "__main__":
    run_collector_loop() 
