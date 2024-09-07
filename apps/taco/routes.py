import os
from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a URL base do Django a partir da variável de ambiente
BASE_URL = os.getenv("ENDPOINT_DJANGO")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

router = APIRouter()

# Rota que consome a API Django do app Taco
@router.get("/taco-data/")
async def get_taco_data():
    url = f"{BASE_URL}/taco/taco/"  # Constrói a URL completa

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)  # Inclua o token no cabeçalho
            response.raise_for_status()  # Levanta exceção se a resposta não for 200
            data = response.json()
            return data
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados do Taco: {str(exc)}")