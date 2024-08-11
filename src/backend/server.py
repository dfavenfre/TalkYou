from fastapi import FastAPI
from helpers.backend_router import functions_router

from datetime import datetime

app = FastAPI(
    title="TalkYou Backend Server v0.1.0",
    summary="TalkYou Application API Documentation",
    version=f"Last Update: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
    contact={
        "name": "TalkYou",
        "url": "https://github.com/dfavenfre/TalkYou",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

app.include_router(functions_router)
