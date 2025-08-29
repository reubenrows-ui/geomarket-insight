from fastapi import FastAPI
from .middleware import setup_middlewares
from .api.v1 import routes_query, routes_data

def create_app():
    app = FastAPI(title="geomarket-insight")
    app.include_router(routes_data.router, prefix="/v1")
    app.include_router(routes_query.router, prefix="/v1")
    setup_middlewares(app)
    return app

app = create_app()
