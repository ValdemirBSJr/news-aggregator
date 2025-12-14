FROM python:3.10-slim
WORKDIR /app

# Copia arquivo de configuracao de pacotes
COPY pyproject.toml .

# Copia todo o código fonte
COPY news_aggregator news_aggregator/

# Instala o pacote
RUN pip install --no-cache-dir .

CMD ["python", "news_aggregator/collectors/newsapi_collector/main.py"]
