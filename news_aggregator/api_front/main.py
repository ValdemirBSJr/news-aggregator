from flask import Flask, render_template, request
from datetime import datetime, date
import random
from news_aggregator.database import connection
import psycopg2

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

if __name__ == '__main__':
   
    app.run(debug=True, host='0.0.0.0', port=5010)