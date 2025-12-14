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

# roda o script
CMD ["python", "news_aggregator/api_front/main.py"]