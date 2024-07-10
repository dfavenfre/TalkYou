from fastapi import FastAPI
from helpers.backend_router import functions_router

app = FastAPI(
    title="TalkYou Backend Server v0.1.0",
    summary="TalkYou Application Endpoints",
    version="0.1.0",
)

app.include_router(functions_router)