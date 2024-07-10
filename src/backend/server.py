from fastapi import FastAPI
from helpers.backend_router import functions_router

app = FastAPI(
    title="Robomentor Service v0.1.0",
    summary="Platform Backend Endpoints",
    version="0.1.0",
)

app.include_router(functions_router)