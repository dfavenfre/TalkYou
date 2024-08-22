from helpers.helper_functions import (
    FetchTranscriptionModel,
    check_transcription,
    FetchVideoLengthModel,
    scrape_video_length,
    scrape_transcription,
)
from helpers.tools import request_identifier, rag_tool
from helpers.constants import selected_thread
from helpers.chatbot import chatbot
from typing import (
    Dict,
    List,
    Union,
    AnyStr,
    Annotated,
    Optional, Any
)
from fastapi import (
    Body,
    Query,
    HTTPException,
    Path,
    Depends, Form
)
from langchain_core.tracers.context import tracing_v2_enabled
from starlette import status
from fastapi import APIRouter
from pydantic import BaseModel, Field
import io
import base64

functions_router = APIRouter()


@functions_router.get(path="/", summary="Check backend connection signal")
async def check_backend_status():
    try:
        return {"status": "Backend Connection Established. Navigate to http://localhost:8000/docs#/"}
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
            description="URL of the YT video",
            min_length=10,
            max_length=100,
            json_schema_extra={
                "example": "https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s"
            }
        ),
        chat_message: Optional[str] = Form(
            default=None,
            description="User's chat message",
            min_length=5,
            max_length=250,
            json_schema_extra={
                "example": "Could you tell me more about the recipe?"
            }
        )
) -> Dict[str, Any]:
    """
    Description:
    ------------
    This endpoint allows users to interact with the AI agent by sending a `chat_message` and
    providing a YouTube `video_url`. The agent will process the input and return a response
    based on the video content only.

    Args:
    ------------
    `video_url: Optional[str]`
        The URL of the YouTube video to be used as context for the chat interaction.
        Example: "https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s"

    `chat_message: Optional[str]`
        The message from the user to be processed by the AI agent.
        Example: "Could you tell me more about the recipe?"

    Return:
    ------------
    `Dict[str, Any]`: A dictionary containing the agent's response to the user's message.
    """
    try:
        payload = {
            "video_url": video_url,
            "chat_message": chat_message
        }

        with tracing_v2_enabled(project_name="TalkYou"):
            response = chatbot.invoke(payload, config=selected_thread)

            if response is not None:
                return response

    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


@functions_router.post(
    path="/process/rag_tool",
    summary="Endpoint for chatting with the scrapped video transcription",
    status_code=status.HTTP_202_ACCEPTED
)
async def chat_with_transcriptions(
        chat_message: str = Form(
            description="User's chat message",
            min_length=5,
            max_length=250,
            example=["Would you tell me which version of the software was supposed to be installed?"]
        )
) -> str:
    """
    Description:
    -------------
    Allows user to chat with the scraped video transcription, that are embedded into
    a vectorstore for RAG process.

    Args:
    -------------
    `chat_message: str` = The chat message sent from the user

    Returns:
    -------------
    A response based on the result of RAG process
    """
    try:
        response = rag_tool._run(chat_message)
        if response is not None:
            return response
    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


@functions_router.post(
    path="/process/identify_request",
    summary='Endpoint for identifying request as either "text" or "image".',
    status_code=status.HTTP_202_ACCEPTED
)
async def identify_request(
        chat_message: str = Form(
            description="User's message, which will be identified",
            min_length=10,
            max_length=250,
            examples=["Could you tell me more about the recipe?"]
        )
) -> Dict[str, Any]:
    """
    Description:
    ------------
    Identifies whether the provided `chat_message` is a text-based or image-based request.

    Args:
    ------------
    `chat_message (str)`: The user's message that needs to be identified as either text or image.

    Return:
    ------------
    `Dict[str, Any]`: A dictionary with the key 'type' indicating whether the request is "text" or "image".
    """
    try:
        response = request_identifier._run(chat_message)

        if response is not None:
            return {"type": response.request_category}

    except Exception as err:
        raise HTTPException(status_code=422, detail=str(err))
