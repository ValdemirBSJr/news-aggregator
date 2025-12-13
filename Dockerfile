FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código para dentro do container
COPY . .

# Expõe porta
EXPOSE 8000

# Comando de execução
CMD ["uvicorn", "api.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
