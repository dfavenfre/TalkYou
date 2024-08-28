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
    """
    Fetches the length of a video given its URL.

    Description:
    ------------
    This endpoint takes a video URL as input and retrieves the length of the video. The length is obtained by using the `scrape_video_length`
    function, which extracts the duration of the video from the video page. The length is returned as a floating-point number representing
    the duration in seconds.

    Args:
    ------------
    `payload (FetchVideoLengthModel)`: The request payload containing the URL of the video for which the length is to be fetched. It should
                                     be a valid URL pointing to a video.

    Returns:
    ------------
    `float`: The length of the video in seconds. If the length is not found, an HTTP 404 error is raised.

    Raises:
    ------------
    `HTTPException`: If an error occurs during the video length retrieval or if the video length cannot be determined, a 404 error is raised
                   with a relevant error message.

    Example:
    ------------
    If the `payload` contains:
        {
            "video_url": "https://www.youtube.com/watch?v=bG4VYwFnU8k"
        }

    And the video length is 120.5 seconds, the function returns: 120.5

    If the video length cannot be determined, the function raises a 404 error.
    """
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
    """
    Checks if the video at the specified URL has a transcription available.

    Description:
    ------------
    This endpoint takes a video URL and checks if a transcription is available for that video. It utilizes the `check_transcription`
    function to determine the presence of a transcription. The result indicates whether a transcription can be found.

    Args:
    ------------
    `payload (FetchTranscriptionModel)`: The request payload containing the URL of the video to check. It should be a valid URL
                                       pointing to a video, encapsulated in a `FetchTranscriptionModel` instance.

    Returns:
    ------------
    `bool`: Returns `True` if a transcription is found, otherwise returns `False`.

    Raises:
    ------------
    `HTTPException`: If an error occurs during the transcription check, a 422 error is raised with the error message.

    Example:
    ------------
    If the `payload` contains:
        {
            "video_url": "https://www.youtube.com/watch?v=bG4VYwFnU8k"
        }

    And a transcription is found, the function returns: `True`

    If no transcription is found, the function returns: `False`
    """
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
    """
    Scrapes the full transcription of a video given its URL.

    Description:
    ------------
    This endpoint takes a video URL as input and returns the full transcription of the video. The transcription is scraped
    from the video and returned in a dictionary where keys are timestamps and values are the corresponding transcription text.

    Args:
    ------------
    `video_url (str)`: The URL of the video to scrape the transcription from. It should be a valid URL pointing to a video,
                     with a minimum length of 10 characters and a maximum length of 100 characters.

    Returns:
    ------------
    `Dict[str, str]`: A dictionary containing the full transcription of the video. Each key is a timestamp in the format "MM:SS",
                    and each value is the corresponding transcription text.

    Raises:
    ------------
    `HTTPException`: If an error occurs during the transcription scraping process, a 404 error is raised with the error message.

    Example:
    ------------
    If the `video_url` is:
    "https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s".

    The function returns:
        {
            "00:05": "Introduction",
            "00:30": "Main discussion starts",
            "01:00": "Conclusion"
        }
    """
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
        raise HTTPException(status_code=500, detail=str(err))


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
) -> Dict[str, Any]:
    """
    Chat with the scraped video transcription.

    Description:
    -------------
    This endpoint allows users to interact with the transcription of a video by sending a chat message. The `rag_tool` processes the chat
    message, retrieves relevant information from the video transcription, and returns a response.

    Args:
    -------------
    `chat_message (str)`: The user's chat message. This message will be used by the `rag_tool` to query the video transcription and
                        generate a response. The message must be between 5 and 250 characters long.

    Returns:
    -------------
    `Dict[str, Any]`: A dictionary containing the response generated by the `rag_tool` based on the chat message and the video transcription.
                    If no response is generated, the function raises an HTTP 404 error.

    Raises:
    -------------
    `HTTPException`: If an error occurs during the processing of the chat message or if no response can be generated, an HTTP 404 error
                   is raised with a relevant error message.
    """
    try:
        response = rag_tool._run(chat_message)
        if response is not None:
            return response

    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


@functions_router.post(
    path="/process/identify_request",
    summary='Endpoint for identifying request as either "information" or "image".',
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
    Identifies the type of user request as either 'information' or 'image'.

    Description:
    ------------
    This endpoint takes a user's chat message and uses the `request_identifier`
    tool to determine whether the request is related to text information or an image.

    Args:
    ------------
    `chat_message: str`: The user's chat message to be analyzed. Must be between 10 and 250 characters long.

    Return:
    ------------
    `Dict[str, Any]`: A dictionary containing the identified request type, either "information" or "image".

    Raises:
    ------------
    `HTTPException`: If an error occurs during request processing, an HTTP 422 error is raised.
    """
    try:
        response = request_identifier._run(chat_message)

        if response is not None:
            return {"type": response.request_category}

    except Exception as err:
        raise HTTPException(status_code=422, detail=str(err))
