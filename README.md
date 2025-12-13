# News Aggregator 📰

**News Aggregator** é um projeto simples que reúne notícias de diferentes fontes (coletores) e expõe uma API/front para consulta. O ambiente padrão utiliza Docker Compose para orquestrar serviços (API, coletores, banco de dados, etc.).

---

## 📚 Visão geral

- `api_front/` — aplicação principal / frontend que expõe a API.
- `collectors/` — diretório com coletores (ex.: `newsapi_collector`, `worldnews_collector`).
- `database/` — scripts de inicialização e migrações para o Postgres.
- `docker-compose.yml` — orquestração por padrão (recomendada).

---

## 🔧 Pré-requisitos

- Docker (recomendado) e Docker Compose (v2 CLI: `docker compose`)
- (Opcional) Python 3.10+ para rodar serviços localmente sem Docker
- Git para publicação no GitHub

---

## ⚡ Rodando o projeto (recomendado: Docker Compose)

1. Copie o arquivo de variáveis de ambiente (se houver um `.env.example`) e ajuste os valores:

```bash
cp .env.example .env
# edite .env conforme necessário
```

2. Inicie os serviços (build + up):

```bash
docker compose up -d --build
```

3. Verifique logs caso necessário:

```bash
docker compose logs -f
# ou apenas do DB
docker compose logs -f db_postgres
```

4. Para parar e remover volumes (útil quando quiser reiniciar a DB do zero):

```bash
docker compose down -v
```

---

## 🧩 Rodando serviços individualmente (sem Docker)

> Use isso apenas para desenvolvimento local ou debugging.

Exemplo para a `api_front`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api_front/requirements.txt
cd api_front
# configurar variáveis de ambiente locais (ex.: DATABASE_URL)
python main.py
```

Cada coletor tem seu próprio `requirements.txt` em `collectors/<collector>/requirements.txt`.

---

## 🗄️ Configuração e inicialização do banco de dados (Postgres)

- Os scripts de inicialização e migração ficam em `database/migrations/`.
- Se você alterar variáveis como `POSTGRES_DB` no `.env`, recomendo derrubar os containers e remover volumes para que o container do Postgres execute os scripts de inicialização novamente:

```bash
docker compose down -v
docker compose up -d --build
```

- Se um serviço reclamar que o banco de dados `newsuser` não existe (ex.: `FATAL: database \"newsuser\" does not exist`):

	- Primeiro verifique seu `.env` e as variáveis `POSTGRES_DB`, `POSTGRES_USER`. Garanta que os nomes sejam consistentes entre a aplicação e o banco.

	- Duas abordagens para resolver:

		1) Ajustar `.env` para que `POSTGRES_DB` seja `newsuser` quando você quiser que esse DB seja criado automaticamente no primeiro start.

		2) Criar o DB manualmente no container do Postgres:

		```bash
		# use o POSTGRES_USER (geralmente 'postgres' ou o valor no .env')
		docker compose exec db_postgres psql -U "$POSTGRES_USER" -c "CREATE DATABASE newsuser;"
		```

	- Se o banco não foi criado por causa de um volume persistente (volume antigo), remova volumes com `docker compose down -v` e suba novamente para forçar entrada dos scripts de inicialização.

---

## ✅ Testes e verificação rápida

- Verifique se a API está externa está respondendo (ex.: `http://localhost:8000` ou porta definida no `docker-compose.yml`).
- Verifique coletores buscando logs ou endpoints de health-check.

---

## 📦 Instalação de dependências (manual)

Para instalar dependências Python (serviço por serviço):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api_front/requirements.txt
pip install -r collectors/newsapi_collector/requirements.txt
pip install -r collectors/worldnews_collector/requirements.txt

```

---

## 🔐 Variáveis de ambiente

Crie um `.env` no root do projeto ou exporte as variáveis antes de rodar os serviços localmente. Exemplo de variáveis importantes:

`POSTGRES_HOST=`
`POSTGRES_PORT=`
`POSTGRES_DB=`
`POSTGRES_USER=`
`POSTGRES_PASSWORD=`
`INTERVAL_UPDATE=` # Intervalo de atualização/coleta das noticias

(aqui eu usei dois serviços o [NewsAPI](https://newsapi.org/) e o [WorldNews](https://www.worldnewsapi.com/), portanto:)
`NEWSAPI_KEY=`
`WORLDNEWS_API_KEY=`

> Recomendo criar um `.env.example` com nomes de variáveis (sem valores sensíveis) e adicionar `.env` ao `.gitignore`.

---

## 📤 Publicação no GitHub

1. Crie um repositório no GitHub.
2. Adicione remote e faça push:

```bash
git remote add origin git@github.com:michelwanderson/news-aggregator.git
git branch -M main
git push -u origin main
```

3. (Opcional) Adicione um `LICENSE` (ex.: MIT) e um arquivo `.github/workflows/ci.yml` se quiser CI (rodar testes, lint e build de imagens).

---

## 🐞 Troubleshooting rápido

- Erro: `FATAL: database \"newsuser\" does not exist` — verifique o `.env` e crie o DB conforme instruções na seção de DB.
- Erro: serviço não inicia — verifique logs com `docker compose logs -f <service>`.
- Erro: variável de ambiente faltando — confira `.env.example` e verifique se `.env` está carregado.

---

## ✍️ Contribuindo

1. Fork e crie uma branch com o fix/feature.
2. Adicione testes sempre que possível.
3. Abra um Pull Request descrevendo a mudança.

---


## 👋 Autor

- Michel Wanderson

---

Se quiser, posso também: criar um `.env.example`, adicionar um script de inicialização de DB mais automático, ou adicionar um workflow de CI básico para rodar checks e builds de imagem. Quer que eu adicione algum desses itens? 🚀
