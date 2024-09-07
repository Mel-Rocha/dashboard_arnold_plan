from fastapi.openapi.utils import get_openapi

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Dashboard Arnold Plan",
        version="1.0.0",
        description="api focused on generating the dashboard for the Arnold Plan",
        routes=app.routes,
    )

    # Define o esquema de segurança Bearer Token
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

        # Garante que "securitySchemes" exista dentro de "components"
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}

        # Define o esquema de segurança Bearer Token
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "API_KEY"  # Pode ser alterado conforme necessário
    }

    # Define os requisitos de segurança para todas as rotas
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema