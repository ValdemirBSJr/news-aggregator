
from news_aggregator.api_front.main import app
import uvicorn
import os

def main():
    """Função principal que inicia a aplicação."""
    # Se quiser rodar com uvicorn programaticamente
    # Ou se preferir usar app.run do Flask direto (menos recomendado para prod, mas ok para dev)
    
    # A request original usava app.run(debug=True, host='0.0.0.0', port=5010)
    # Vamos manter a compatibilidade ou melhorar?
    # O user usava: app.run(debug=True, host='0.0.0.0', port=5010)
    
    # Vamos tentar respeitar o que estava no main.py original, 
    # mas chamando a função se ela existir, ou rodando o app.
    
    print("Iniciando News Aggregator...")
    app.run(debug=True, host='0.0.0.0', port=5010)

if __name__ == "__main__":
    main()
