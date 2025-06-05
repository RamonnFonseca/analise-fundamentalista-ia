# Futuras configurações da aplicação, como chaves de API, URLs de banco de dados, etc.
# Exemplo:
# from pydantic_settings import BaseSettings
# class Settings(BaseSettings):
#     APP_NAME: str = "Minha API"
#     DATABASE_URL: str
#     OPENAI_API_KEY: str
#     class Config:
#         env_file = ".env"
# settings = Settings() 

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Análise Fundamentalista API"
    
    # Chave de API para o serviço do Google Gemini
    # Será lida da variável de ambiente GEMINI_API_KEY
    GEMINI_API_KEY: str

    class Config:
        # O Pydantic irá procurar por um arquivo .env e carregar as variáveis dele
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Cria uma instância única das configurações que será usada em toda a aplicação
settings = Settings() 