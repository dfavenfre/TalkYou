from typing import (
    TypedDict,
    Union,
    Tuple,
    Dict,
    List
)
from helpers.tools import (
    transcription_checker,
    video_length_checker,
    transcription_scrapper
)
from helpers.helper_functions import (
    create_empty_vectorstore,
    create_vectorstore_index
)
import tempfile
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
    transcription_text: str
    full_transcription: Dict[str, str]
    vectorstore_path: str
    chat_message: str


def check_video_length(state):
    print("---BEGIN: CHECKING VIDEO LENGTH---")
    video_url = state["video_url"]

    try:
        length = video_length_checker(video_url)
        print(F"---PROCESS: VIDEO LENGTH IS -> {length}")

        if length >= 5:
            return {"video_length": ">5"}
        else:
            return {"video_length": "<5"}

    except Exception as err:
        raise Exception(f"Something went wrong during scrapping -> {err}")


def selenium_or_pytube(state):
    video_length = state["video_length"]

    if video_length == "<5":
        print("---PROCESS: MOVING ON WITH SELENIUM---")
        return "Selenium"

    else:
        print("---PROCESS: MOVING ON WITH PYTUBE---")
        return "Pytube"


def download_with_pytube(state):
    video_url = state["video_url"]
    print("---PROCESS: DOWNLOADING VIDEO WITH PYTUBE---")
    return {"transcription_text": "..."}


def check_transcription_element(state):
    video_url = state["video_url"]
    print("---PROCESS: CHECKING TRANSCRIPTION ELEMENT---")

    transcription_found = transcription_checker(video_url)

    if transcription_found:
        print("---CHECKING: TRANSCRIPTION FOUND---")
        return {"has_transcription": True}

    else:
        print("---CHECKING: TRANSCRIPTION NOT FOUND---")
        return {"has_transcription": False}


def scrape_or_download(state):
    has_transcription = state["has_transcription"]
    print("---DECISION: SCRAPING OR DOWNLOAD---")
    if has_transcription:
        print("---PROCESS: MOVING ON WITH SCRAPPING---")
        return "Scrape"

    else:
        print("---PROCESS: MOVING ON WITH PYTUBE---")
        return "Download"


def extract_transcription(state):
    print("---PROCESS: EXTRACTING TRANSCRIPTION---")
    video_url = state["video_url"]

    full_transcription = transcription_scrapper._run(video_url)
    parsed_transcription = "".join(full_transcription.values())
    return {
        "transcription_text": parsed_transcription,
        "full_transcription": full_transcription
    }


def init_vectorstore(state):
    print("---PROCESS: INITIALIZING VECTORSTORE---")
    transcription = state["transcription_text"]
    empty_vectorstore = create_empty_vectorstore()
    updated_vectorstore = create_vectorstore_index(vectorstore=empty_vectorstore, documents=transcription)
    updated_vectorstore.save_local("faiss_vectorstore")
    print("---PROCESS: VECTORSTORE READY---")
    return {
        "vectorstore_build": True,
        "vectorstore_path": "faiss_vectorstore"
    }
