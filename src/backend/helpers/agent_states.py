from sklearn.metrics.pairwise import cosine_similarity
from langgraph.graph import MessagesState
from typing import (
    TypedDict,
    Union,
    Tuple,
    Dict,
    List, Any
)
from helpers.tools import (
    transcription_checker,
    video_length_checker,
    transcription_scrapper,
    request_identifier,
    screenshot_tool,
    rag_tool
)
from helpers.helper_functions import (
    create_empty_vectorstore,
    create_vectorstore_index,
    text_embedding_v3_small,
    search_timestamp,
    take_screenshot
)
import tempfile
import asyncio
import os

class GraphState(TypedDict):
    """
    Description:
    -------------
    Represents the Graph State of our Chatbot Model
    """
    identified_query: str
    video_url: str
    vectorstore_build: bool
    video_length: int
    has_transcription: bool
    transcription_text: str
    full_transcription: Dict[str, str]
    vectorstore_path: str
    chat_message: str
    identified_request: str
    response: str
    search_result: Dict[Any, Any]
    total_seconds: int
    updated_url: str
    screenshot_base64: Any


def check_video_length(state):
    print("---BEGIN: CHECKING VIDEO LENGTH---")
    video_url = state["video_url"]

    try:
        length = video_length_checker(video_url)
        print(F"---PROCESS: VIDEO LENGTH IS -> {length}")

        if length >= 20:
            return {"video_length": ">20"}
        else:
            return {"video_length": "<20"}

    except Exception as err:
        raise Exception(f"Something went wrong during scrapping -> {err}")


def selenium_or_pytube(state):
    video_length = state["video_length"]

    if video_length == "<20":
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
    parsed_transcription = ". ".join(full_transcription.values())
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
        "vectorstore_path": "./faiss_vectorstore"
    }


def load_vectorstore_states(state):
    print("---CHECKING: SEARCHING FOR A VECTORSTORE---")
    vectorstore_path = state["vectorstore_path"]

    if vectorstore_path is not None:
        return {"vectorstore_build": True}
    else:
        return {"vectorstore_build": False}


def check_vectorstore_presence(state):
    is_built = state["vectorstore_build"]
    if is_built:
        print("---DECISION: VECTORSTORE FOUND...PROCEEDING TO CHATBOT---")
        return "Chatbot"

    else:
        print("---DECISION: VECTORSTORE NOT FOUND---")
        return "Fetch Data"


def query_identifier(states):
    print("---PROCESS: QUERY IDENTIFIER---")
    chat_message = states["chat_message"]

    category = request_identifier._run(chat_message)

    if category.request_category == "information":
        print(f"---PROCESS: IDENTIFIED THE QUERY AS -> {category.request_category}---")
        return {"identified_request": "information"}
    else:
        print(f"---PROCESS: IDENTIFIED THE QUERY AS -> {category.request_category}---")
        return {"identified_request": "image"}


def check_request_type(state):
    identified_request = state["identified_request"]

    if identified_request == "information":
        return "Information"
    else:
        return "Image"


def proceed_to_rag(state):
    print(f"---PROCESS: GENERATING THE ANSWER---")
    chat_message = state["chat_message"]
    response = rag_tool._run(chat_message)

    return {"response": response}


def proceed_to_image_retrieval(state):
    full_transcription = state["full_transcription"]
    chat_message = state["chat_message"]
    video_url = state["video_url"]

    total_seconds = search_timestamp(full_transcription, chat_message)
    if "&t=" in video_url:
        pattern_index = video_url.find("&t=")
        video_url = video_url[:pattern_index]
        updated_url = video_url + f"&t={total_seconds}s"

    else:
        updated_url = video_url + f"&t={total_seconds}s"

    return {"total_seconds": total_seconds, "updated_url": updated_url}


def take_video_screenshot(state):
    updated_url = state["updated_url"]
    base64_image = screenshot_tool.run(updated_url)
    return {"screenshot_base64": base64_image}
