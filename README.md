# Patent AI Lab API

API de leitura para o projeto Patent AI Lab.

## Como executar

1. Copie as variáveis de ambiente do projeto principal para o diretório `api/`.
2. Defina `API_KEY` se quiser proteger rotas sensíveis.
3. Instale dependências:

```bash
cd api
pip install -r requirements.txt
```

4. Execute a API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker (opcional)

Build and run a minimal container:

```bash
cd api
docker build -t patent-ai-api .
docker run -p 80:80 --env-file .env --rm -e PORT=80 patent-ai-api
```

Deploy notes for Render/Railway:

- If using Docker, push the image or connect the repo and use the provided `Dockerfile`.
- If using the platform's build (no Docker), add the start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers` or use the included `Procfile`.
- Set environment variables (DB_HOST, DB_USER, DB_PASS, API_KEY, etc.) in the platform's dashboard—do not commit `.env`.

## Endpoints

- `GET /health`
- `GET /terms`
- `GET /terms/{term}/timeseries`
- `GET /terms/{term}/correlations`
- `GET /terms/{term}/indicators`
- `GET /ranking`
- `GET /predictions/{term}`
- `GET /dictionary` (protegido por `X-API-Key`)
