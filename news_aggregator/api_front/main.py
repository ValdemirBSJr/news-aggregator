from flask import Flask, render_template, request
from datetime import datetime, date
import random
from news_aggregator.database import connection
import psycopg2
import sqlite3

app = Flask(__name__)

# --- Configurações do Banco de Dados ---
# Usamos o connection.py agora

def get_news_from_db(target_date: date):
    """Conecta ao Banco (PG ou SQLite) e busca notícias."""
    conn = None
    noticias = []
    try:
        # Tenta estabelecer a conexão via nosso wrapper
        conn = connection.get_db_connection()
        
        # Cria um cursor (se for sqlite, já configuramos row_factory)
        # Se for PG, precisamos garantir que retorne algo acessível via chave
        if connection.get_db_type() == 'postgres':
             cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
             cur = conn.cursor()

        # Query adaptada
        # SQLite não tem ::date, usa date()
        # Postgres tem ::date.
        if connection.get_db_type() == 'postgres':
            query = "SELECT id, title, source, url, description FROM news_raw WHERE published_at::date = %s ORDER BY published_at DESC LIMIT 20;"
            cur.execute(query, (target_date,))
        else:
            # SQLite: assumindo que published_at está string 'YYYY-MM-DD HH:MM:SS'
            # A função date() do sqlite extrai a data.
            # O placeholder é ? em vez de %s (tratado pelo convert_param_style ou manualmente aqui)
            query = "SELECT id, title, source, url, description FROM news_raw WHERE date(published_at) = ? ORDER BY published_at DESC LIMIT 20;"
            cur.execute(query, (target_date.strftime("%Y-%m-%d"),))

        # Busca todos os resultados
        resultados = cur.fetchall()

        # Normaliza resultados para dict se não vierem (SQLite row factory já ajuda)
        # Se for PG RealDictCursor, já é dict-like.
        
        for row in resultados:
            # Se for sqlite Row ou PG RealDictRow, podemos converter pra dict ou acessar direto
            noticias.append(dict(row))

        cur.close()

    except Exception as error:
        print(f"Erro ao conectar ou buscar dados: {error}")
        noticias = [] 
        
    finally:
        # Fecha a conexão se ela foi aberta
        if conn:
            conn.close()
            
    return noticias

@app.route('/')
def home():
    """Rota principal que busca as notícias e renderiza o template."""
    # Pega a data da URL (?date=YYYY-MM-DD), se não houver, usa a data atual.
    selected_date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        # Se a data for inválida, usa a data atual como padrão.
        selected_date = datetime.now().date()

    noticias = get_news_from_db(selected_date)

    
    # Numeros aleatórios para edição
    edicao_random = random.uniform(0.0, 9.9)
    edicao_random = round(edicao_random, 3)

    # Formata a data para exibição no template
    dia_num = selected_date.strftime("%d")
    dia_da_semana = selected_date.strftime("%A")
    mes = selected_date.strftime("%B")
    ano_atual = selected_date.strftime("%Y")

    # Renderiza o template 'index.html', passando a lista de notícias
    return render_template('index.html', news_items=noticias, ano=ano_atual, dia=dia_num, mes=mes, dia_da_semana=dia_da_semana, edicao=edicao_random, selected_date=selected_date.strftime("%Y-%m-%d"))

from news_aggregator.ai import analyzers, llm
import json

# ... existing imports ...

def get_article_by_id(article_id):
    conn = connection.get_db_connection()
    try:
        if connection.get_db_type() == 'postgres':
             cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
             conn.row_factory = sqlite3.Row
             cur = conn.cursor()
             
        query = "SELECT * FROM news_raw WHERE id = %s"
        query = connection.convert_param_style(query)
        cur.execute(query, (article_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

def get_candidate_news(limit=100):
    """Fetch recent news to compare against."""
    conn = connection.get_db_connection()
    try:
        if connection.get_db_type() == 'postgres':
             cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
             conn.row_factory = sqlite3.Row
             cur = conn.cursor()
             
        # Fetch last 100 items for comparison
        query = "SELECT * FROM news_raw ORDER BY published_at DESC LIMIT %s"
        query = connection.convert_param_style(query)
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.route('/api/translate', methods=['POST'])
def api_translate():
    data = request.json
    text = data.get('text')
    if not text:
        return {"error": "No text provided"}, 400
    
    translation = llm.translate_content(text)
    return {"translation": translation}

@app.route('/api/related', methods=['POST'])
def api_related():
    data = request.json
    article_id = data.get('id')
    if not article_id:
        return {"error": "No id provided"}, 400
        
    current_article = get_article_by_id(article_id)
    if not current_article:
        return {"error": "Article not found"}, 404
        
    # Get text to compare
    current_text = f"{current_article.get('title', '')} {current_article.get('description', '')} {current_article.get('content', '')}"
    
    # Get candidates (exclude self is handled by similarity logic usually or explicit check)
    all_news = get_candidate_news(limit=50) # Keep it fast
    # Filter out self
    candidates = [n for n in all_news if str(n.get('id')) != str(article_id)]
    
    related = analyzers.find_related_news(current_text, candidates, limit=3)
    
    if not related:
        return {
            "summary": "Nenhuma notícia relacionada encontrada recentemente.",
            "links": []
        }
    
    # Summarize related content
    texts_to_summarize = [f"{r.get('title')}: {r.get('description') or r.get('content') or ''}" for r in related]
    summary = llm.generate_summary(texts_to_summarize)
    
    # Format links
    links = []
    for r in related:
        links.append({
            "title": r.get('title'),
            "url": r.get('url'),
            "date": str(r.get('published_at'))
        })
        
    return {
        "summary": summary,
        "links": links
    }

if __name__ == '__main__':
   
    app.run(debug=False, host='0.0.0.0', port=5010)