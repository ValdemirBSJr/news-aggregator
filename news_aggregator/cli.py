from news_aggregator.api_front.main import app
from news_aggregator.collectors.newsapi_collector.main import run_collector_loop as run_newsapi
from news_aggregator.collectors.worldnews_collector.main import run_collector_loop as run_worldnews
import threading
import os

def main():
    """Função principal que inicia a aplicação e os coletores (modo local)."""
    
    # Inicia coletores em threads background (daemon=True morrem quando o app fecha)
    # Isso é ideal para o modo local simplificado. 
    # Em produção via Docker, os serviços rodam separados e esse script do Flask roda isolado
    # (mas no Docker este script não é chamado para os coletores, e sim main.py direto deles)
    
    print("Iniciando coletores em background...")
    t1 = threading.Thread(target=run_newsapi, daemon=True)
    t1.start()
    
    t2 = threading.Thread(target=run_worldnews, daemon=True)
    t2.start()

    print("Iniciando News Aggregator Web App...")
    # debug=True do Flask pode causar reload e duplicar threads se não cuidar, 
    # use_reloader=False ajuda a evitar duplicidade em dev simples,
    # mas remove o hot-reload. Vamos deixar padrão por enquanto.
    app.run(debug=True, host='0.0.0.0', port=5010, use_reloader=False)

if __name__ == "__main__":
    main()
