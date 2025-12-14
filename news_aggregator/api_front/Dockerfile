FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y tzdata && \
    rm -rf /var/lib/apt/lists/*

ENV TZ=America/Sao_Paulo


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

CMD ["python", "main.py"]