import tempfile
from typing import (
    TypedDict,
    Union,
    Tuple,
    Dict,
    List
)
from helpers.tools import transcription_checker, video_length_checker
import asyncio


class GraphState(TypedDict):
    """
    Description:
    -------------
    Represents the Graph State of our Chatbot Model
    """
    video_url: str
    vectorstore_build: bool
    video_length: int
    has_transcription: bool
    transcription: str


def check_video_length(state):
    video_url = state["video_url"]

    try:
        length = transcription_checker(video_url)

        if length >= 5:
            return {"video_length": ">5"}
        else:
            return {"video_length": "<5"}

    except Exception as err:
        raise Exception(f"Something went wrong during scrapping -> {err}")


def selenium_or_pytube(state):
    video_length = state["video_length"]

    if video_length >= 5:
        return "Selenium"

    else:
        return "Pytube"


def download_with_pytube(state):
    video_url = state["video_url"]

    return {"transcription": "..."}


def check_transcription_element(state):
    video_url = state["video_url"]

    try:
        transcription_found = transcription_checker(video_url)

        if transcription_found:
            return {"has_transcription": True}

        else:
            return {"has_transcription": False}

    except:
        raise Exception("Something went wrong during scrapping")


def scrape_or_download(state):
    has_transcription = state["has_transcription"]

    if has_transcription:
        return "Scrape"

    else:
        return "Download"


def extract_transcription(state):
    video_url = state["video_url"]

    return {"transcription": "..."}


def create_vectorstore(state):
    transcription = state["transcription"]

    return {"vectorstore_build": True}


