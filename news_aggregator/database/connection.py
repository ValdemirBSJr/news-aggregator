import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to track which DB we are using
_DB_TYPE = None

def get_db_type():
    """Returns 'postgres' or 'sqlite'."""
    global _DB_TYPE
    if _DB_TYPE is None:
        get_db_connection().close() # Init and check
    return _DB_TYPE

def _init_sqlite(db_path="news.db"):
    """Initialize SQLite database with the schema."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cur = conn.cursor()
    
    # SQLite schema - slightly different from Postgres
    # UUID generation in SQLite usually handled by application or ignoring it for simple auto-inc, 
    # but here we keep UUID as text or generate it in python.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS news_raw (
        id TEXT PRIMARY KEY,
        source TEXT,
        title TEXT,
        description TEXT,
        url TEXT UNIQUE,
        published_at TIMESTAMP,
        content TEXT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    return conn

def get_db_connection():
    """
    Tries to connect to PostgreSQL using environment variables.
    If it fails (vars missing or connection refused), falls back to SQLite.
    """
    global _DB_TYPE
    
    # 1. Try Postgres
    pg_host = os.getenv('POSTGRES_HOST')
    # Simple heuristic: if no host configured, don't even try (fast fail to sqlite)
    # But user asked to verify service. So we interpret "verify" as "try authenticate".
    
    if pg_host:
        try:
            dsn = (
                f"host={os.getenv('POSTGRES_HOST')} "
                f"port={os.getenv('POSTGRES_PORT', 5432)} "
                f"dbname={os.getenv('POSTGRES_DB')} "
                f"user={os.getenv('POSTGRES_USER')} "
                f"password={os.getenv('POSTGRES_PASSWORD')}"
            )
            # Short timeout to avoid hanging if IP is wrong but reachable
            conn = psycopg2.connect(dsn, connect_timeout=3)
            if _DB_TYPE is None:
                logger.info("✅ Connected to PostgreSQL.")
                _DB_TYPE = 'postgres'
            return conn
        except psycopg2.OperationalError as e:
            if _DB_TYPE is None:
                logger.warning(f"⚠️ PostgreSQL unavailable ({e}). ⚠️\n👉 Falling back to SQLite (local mode).")
    
    # 2. Fallback to SQLite
    if _DB_TYPE is None:
        logger.info("Using SQLite database (news.db).")
        _DB_TYPE = 'sqlite'
        
    return _init_sqlite()

def convert_param_style(sql):
    """
    Converts Postgres style (%s) to SQLite style (?) if needed.
    """
    if get_db_type() == 'sqlite':
        return sql.replace('%s', '?')
    return sql
