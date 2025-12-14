import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configura um log básico para tracert da app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag global para vermos qual db vamos usar
_DB_TYPE = None

def get_db_type():
    """Retorna 'postgres' ou 'sqlite'."""
    global _DB_TYPE
    if _DB_TYPE is None:
        get_db_connection().close()
    return _DB_TYPE

def _init_sqlite(db_path="news.db"):
    """Inicializa o banco de dados SQLite com o schema."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cur = conn.cursor()
    
    # SQLite schema - Levemente diferente do Postgres
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
    Tenta conectar ao PostgreSQL usando variáveis de ambiente.
    Se falhar (vars missing or connection refused), falls back para SQLite.
    """
    global _DB_TYPE
    
    # Tentamos o postgres
    pg_host = os.getenv('POSTGRES_HOST')
    # Verificamos se nao existe a variavel do postgres no container.
    
    if pg_host:
        try:
            dsn = (
                f"host={os.getenv('POSTGRES_HOST')} "
                f"port={os.getenv('POSTGRES_PORT', 5432)} "
                f"dbname={os.getenv('POSTGRES_DB')} "
                f"user={os.getenv('POSTGRES_USER')} "
                f"password={os.getenv('POSTGRES_PASSWORD')}"
            )
            # verificamos se o ip do postgres esta acessivel.
            conn = psycopg2.connect(dsn, connect_timeout=3)
            if _DB_TYPE is None:
                logger.info("✅ Connected to PostgreSQL.")
                _DB_TYPE = 'postgres'
            return conn
        except psycopg2.OperationalError as e:
            if _DB_TYPE is None:
                logger.warning(f"⚠️ PostgreSQL unavailable ({e}). ⚠️\n👉 Falling back to SQLite (local mode).")
    
    # Se nao existir o postgres, usamos o sqlite(execução local)
    if _DB_TYPE is None:
        logger.info("Using SQLite database (news.db).")
        _DB_TYPE = 'sqlite'
        
    return _init_sqlite()

def convert_param_style(sql):
    """
    Converte o estilo de paramentro do postgres para sqlite, caso necessario.
    """
    if get_db_type() == 'sqlite':
        return sql.replace('%s', '?')
    return sql
