from fastapi import FastAPI
from app.api.v1 import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Uma API para buscar dados da CVM, processar com IA e gerar relatórios.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuração do CORS
# Isso permite que um frontend rodando em qualquer origem (*) acesse a API.
# Para produção, você deve restringir a lista de origens permitidas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Análise Fundamentalista com IA!"}

# Aqui registraremos os routers da API v1 posteriormente
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 