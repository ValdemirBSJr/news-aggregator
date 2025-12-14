import os
import psycopg2
from flask import Flask, render_template, request
from datetime import datetime, date
import random

app = Flask(__name__)

# --- Configurações do Banco de Dados PostgreSQL ---
DB_DSN = (
    f"host={os.getenv('POSTGRES_HOST')} "
    f"port={os.getenv('POSTGRES_PORT',5432)} "
    f"dbname={os.getenv('POSTGRES_DB')} "
    f"user={os.getenv('POSTGRES_USER')} "
    f"password={os.getenv('POSTGRES_PASSWORD')}"
)


def get_news_from_db(target_date: date):
    """Conecta ao PostgreSQL e busca todas as notícias da tabela news_raw."""
    conn = None
    noticias = []
    try:
        # Tenta estabelecer a conexão
        conn = psycopg2.connect(DB_DSN)
        # Cria um cursor para executar comandos SQL
        cur = conn.cursor()

        # Executa a query para buscar as colunas desejadas
        query = "SELECT id, title, source, url, description FROM news_raw WHERE published_at::date = %s ORDER BY published_at DESC LIMIT 20;"
        cur.execute(query, (target_date,))

        # Busca todos os resultados
        resultados = cur.fetchall()

        # Obtém os nomes das colunas para criar uma lista de dicionários
        column_names = [desc[0] for desc in cur.description]
        
        # Converte os resultados em uma lista de dicionários para fácil acesso no template
        for row in resultados:
            noticias.append(dict(zip(column_names, row)))

        # Fecha o cursor
        cur.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao conectar ou buscar dados do PostgreSQL: {error}")
        # Em um ambiente de produção, você pode querer logar isso e mostrar uma mensagem de erro amigável.
        noticias = [] # Retorna lista vazia em caso de erro
        
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