from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.docs.custom_openapi import custom_openapi  # Importa o custom OpenAPI
from apps.taco.routes import router as taco_router  # Importa as rotas do Taco
from apps.docs import routes as docs_router  # Importa as rotas do dashboard
from apps.auth.middlewares import AuthMiddleware  # Middleware de autenticação

# Função para criar a aplicação FastAPI
def create_application() -> FastAPI:
    application = FastAPI()

    # Adiciona middlewares
    application.add_middleware(AuthMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
        allow_headers=["*"]
    )

    # Inclui as rotas do dashboard e do Taco
    application.include_router(docs_router.router, tags=['dashboard'])
    application.include_router(taco_router, prefix="/taco", tags=["taco"])

    return application


# Instancia a aplicação
app = create_application()

# Define o custom OpenAPI
app.openapi = lambda: custom_openapi(app)
