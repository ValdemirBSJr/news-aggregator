FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y tzdata && \
    rm -rf /var/lib/apt/lists/*

ENV TZ=America/Sao_Paulo

# Copia arquivo de configuracao de pacotes
COPY pyproject.toml .

# Copia todo o código fonte
COPY news_aggregator news_aggregator/

# Instala o pacote e suas dependencias
RUN pip install --no-cache-dir .

# Executa usando o modulo (forma mais segura) ou o script direto.
# Como o main.py original estava em api_front/main.py, podemos chamar via modulo se ele estiver adaptado, 
# mas como nao alteramos para ser `python -m news_aggregator.api_front`, vamos usar o caminho relativo,
# sabendo que o pacote está instalado no path.
CMD ["python", "news_aggregator/api_front/main.py"]