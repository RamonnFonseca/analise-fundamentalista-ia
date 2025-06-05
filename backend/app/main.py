from fastapi import FastAPI
from app.api.v1 import api_router

app = FastAPI(
    title="API de Análise Fundamentalista CVM",
    description="Uma API para buscar dados da CVM, processar com IA e gerar relatórios.",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API de Análise Fundamentalista CVM!"}

# Aqui registraremos os routers da API v1 posteriormente
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 