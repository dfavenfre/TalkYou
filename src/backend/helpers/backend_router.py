from typing import (
    Dict,
    List,
    Union,
    AnyStr,
    Annotated,
    Optional
)
from fastapi import (
    Body,
    Query,
    HTTPException,
    Path,
    Depends
)

from langchain_core.tracers.context import tracing_v2_enabled
from sqlalchemy.orm import Session
from sqlalchemy import event
from starlette import status
from fastapi import APIRouter
from pydantic import BaseModel, Field
import io
import base64

functions_router = APIRouter()


@functions_router.get(path="/backend_check", summary="Check backend connection signal")
async def check_backend_status():
    try:
        return {"status": "Backend Connection Established"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
