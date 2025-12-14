from news_aggregator.api_front.main import app
from news_aggregator.collectors.newsapi_collector.main import run_collector_loop as run_newsapi
from news_aggregator.collectors.worldnews_collector.main import run_collector_loop as run_worldnews
import threading
import os
from news_aggregator.ai import analyzers

def preload_models():
    """Carrega modelos Spacy em background para nao travar o primeiro request."""
    print("Pre-loading AI models (Light)...")
    analyzers.get_model('en')
    analyzers.get_model('pt')
    print("AI models loaded.")

def main():
    """Função principal que inicia a aplicação e os coletores (modo local).
       Em modo container (server), os coletores rodam em containers separados.
    """
    
    
    print("Iniciando coletores em background...")
    t1 = threading.Thread(target=run_newsapi, daemon=True)
    t1.start()
    
    t2 = threading.Thread(target=run_worldnews, daemon=True)
    t2.start()

    print("Iniciando News Aggregator Web App...")
    # debug=True do Flask pode causar reload e duplicar threads se não cuidar, 
    # use_reloader=False ajuda a evitar duplicidade em dev simples,
    # mas remove o hot-reload.
    app.run(debug=False, host='0.0.0.0', port=5010, use_reloader=False)

if __name__ == "__main__":
    main()
