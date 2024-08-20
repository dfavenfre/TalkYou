from helpers.helper_functions import (
    FetchTranscriptionModel,
    check_transcription,
    FetchVideoLengthModel,
    scrape_video_length,
    scrape_transcription
)
from helpers.chatbot import chatbot
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
    Depends, Form
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


@functions_router.post(
    path="/fetch/get_video_length",
    summary="Fetch video length",
    status_code=status.HTTP_202_ACCEPTED
)
async def fetch_video_length(payload: FetchVideoLengthModel):
    try:
        video_length = scrape_video_length(payload.video_url)

        if video_length is not None:
            return video_length

        else:
            raise HTTPException(status_code=404, detail="---CHECK THE RETURNED VALUE---")

    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


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

        if found_transcription:
            return found_transcription

        else:
            return False

    except Exception as err:
        print(f"Error occurred: {err}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )


@functions_router.post(
    path="/fetch/video_transcription",
    summary='Scrapes full video transcription',
    status_code=status.HTTP_202_ACCEPTED
)
async def fetch_video_transcription(
        video_url: str = Form(
            ...,
            description="URL of the video that you want to scrape the transcription of",
            min_length=10,
            max_length=100,
            json_schema_extra={
                "example": "https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s"
            }
        )
) -> Dict[str, str]:
    try:
        full_transcription = scrape_transcription(video_url)

        if full_transcription is not None:
            return full_transcription

    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


@functions_router.post(
    path="/process/converse_with_agent",
    summary='Endpoint for chatting with our agent',
    status_code=status.HTTP_202_ACCEPTED
)
async def converse_with_agent(
        video_url: Optional[str] = Form(
            default=None,
            description="url of the YT video",
            min_length=10,
            max_length=100,
            json_schema_extra={
                "example": "https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s"
            }
        )
):
    try:
        payload = {
            "video_url": video_url
        }

        with tracing_v2_enabled(project_name="TalkYou"):
            response = chatbot.invoke(payload)

            if response is not None:
                return response

    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))
