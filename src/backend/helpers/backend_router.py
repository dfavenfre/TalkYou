from helpers.helper_functions import FetchTranscriptionModel, check_transcription

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


@functions_router.post(
    path="/fetch/check_transcription",
    summary='Checks if there is video transcription',
    status_code=status.HTTP_202_ACCEPTED
)
async def fetch_transcription_element(
        payload: FetchTranscriptionModel
):
    try:
        found_transcription = check_transcription(payload.video_url)

        if found_transcription is not None:
            data = found_transcription.json()
            return data

        return found_transcription

    except Exception as err:
        print(f"Error occurred: {err}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )
