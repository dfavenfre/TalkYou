import os.path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from helpers.constants import (service, options, driver, text_embedding_v3_small)
from typing import Optional, Dict, Tuple, Union, Any, List, AnyStr
from pydantic import BaseModel, Field
from langchain_community.docstore.in_memory import InMemoryDocstore
from sklearn.metrics.pairwise import cosine_similarity
from faiss import IndexFlatL2
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import yaml
import base64


class ScreenshotModel(BaseModel):
    """
    Model for specifying the URL of a video for which a screenshot is to be taken.

    Description:
    ------------
    This model represents the request payload for taking a screenshot of a video. It includes a single field,
    `video_url`, which specifies the URL of the video from which the screenshot will be taken.

    Attributes:
    ------------
    video_url (str): The URL of the video for which the screenshot is requested. It should be a valid URL pointing to
                     a video, with a minimum length of 10 characters and a maximum length of 100 characters.

    Example:
    ------------
    An example of the request payload:
    {
        "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
    }
    """
    video_url: str = Field(
        description="URL of the video that you want to take screenshot of",
        min_length=10,
        max_length=100,
    )


class RagToolModel(BaseModel):
    """
    Model for handling user chat messages in the RAG (Retrieval-Augmented Generation) tool.

    Description:
    ------------
    This model represents the request payload for the RAG tool. It includes a single field, `chat_message`, which
    captures the user's chat message. This message is used as input for the RAG tool to process and generate responses.

    Attributes:
    ------------
    chat_message (str): The user's chat message. It must be between 5 and 250 characters long.

    Example:
    ------------
    An example of the request payload:
    {
        "chat_message": "Would you tell me which version of the software was supposed to be installed?"
    }
    """
    chat_message: str = Field(
        description="User's chat message",
        min_length=5,
        max_length=250,
    )

    class Config:
        schema_extra = {
            "example": {
                "chat_message": "Would you tell me which version of the software was supposed to be installed?",
            }
        }


class RequestIdentifierModel(BaseModel):
    """
    Model for identifying the type of request based on a chat message.

    Description:
    ------------
    This model represents the request payload for identifying the type of request from a user's chat message. It includes
    a single field, `chat_message`, which is used to determine the type of request based on the content of the message.

    Attributes:
    ------------
    chat_message (str): The user's chat message, which will be used to identify the request type. It must be between
                        5 and 250 characters long.

    Example:
    ------------
    An example of the request payload:
    {
        "chat_message": "Would you show me the picture of the pasta?"
    }
    """
    chat_message: str = Field(
        description="User's chat message, which will be used to identify request type",
        min_length=5,
        max_length=250,
    )

    class Config:
        schema_extra = {
            "example": {
                "chat_message": "Would you show me the picture of the pasta?",
            }
        }


class RequestParser(BaseModel):
    """
    Model for categorizing requests based on their type.

    Description:
    ------------
    This model represents the request payload for categorizing requests. It includes a single field, `request_category`,
    which specifies the category of the request. The category can be either 'information' or 'image'.

    Attributes:
    ------------
    request_category (str): The category of the request, which should be either 'information' or 'image'.

    Example:
    ------------
    An example of the request payload:
    {
        "request_category": "information"
    }
    """
    request_category: str = Field(
        description="Category of the request, which is either 'information' or 'image'",
    )


class ScrapeTranscriptions(BaseModel):
    """
    Model for scraping the transcription of a video from its URL.

    Description:
    ------------
    This model represents the request payload for scraping the transcription of a video. It includes a single field,
    `video_url`, which specifies the URL of the video from which the transcription will be scraped.

    Attributes:
    ------------
    video_url (str): The URL of the video to scrape the transcription from. It should be a valid URL pointing to a
                     YouTube video, with a minimum length of 10 characters and a maximum length of 100 characters.

    Example:
    ------------
    An example of the request payload:
    {
        "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
    }
    """
    video_url: str = Field(
        description="URL of the video that you want to scrape the transcription of",
        min_length=10,
        max_length=100,
    )


class FetchTranscriptionModel(BaseModel):
    """
    Model for fetching the transcription of a video from its URL.

    Description:
    ------------
    This model represents the request payload for fetching the transcription of a video. It includes a single field,
    `video_url`, which specifies the URL of the video from which the transcription will be fetched.

    Attributes:
    ------------
    video_url (str): The URL of the video for which the transcription is to be fetched. It should be a valid URL pointing
                     to a YouTube video, with a minimum length of 10 characters and a maximum length of 50 characters.

    Example:
    ------------
    An example of the request payload:
    {
        "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
    }
    """
    video_url: str = Field(
        description="URL of the video you want to fetch.",
        min_length=10,
        max_length=50,
    )

    class Config:
        schema_extra = {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
            }
        }


class FetchVideoLengthModel(BaseModel):
    """
    Model for fetching the length of a video from its URL.

    Description:
    ------------
    This model is used to represent the request payload for fetching the length of a video. It includes a single field,
    `video_url`, which specifies the URL of the video to be checked.

    Attributes:
    ------------
    video_url (str): The URL of the video for which the length is to be fetched. It should be a valid URL pointing to a
                     YouTube video, with a minimum length of 10 characters and a maximum length of 50 characters.

    Example:
    ------------
    An example of the request payload:
    {
        "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
    }
    """
    video_url: str = Field(
        description="URL of the video you want to check the length of",
        min_length=10,
        max_length=50,
    )

    class Config:
        schema_extra = {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
            }
        }


def scrape_video_length(
        video_url: str
) -> Union[float, bool]:
    """
    Scrapes the length of a YouTube video from the provided URL.

    Description:
    ------------
    This function navigates to the given YouTube video URL and retrieves the video's duration. The duration is extracted
    from the video's time display element. If the duration is successfully retrieved, it is returned as a float representing
    the total length in minutes. If the duration cannot be retrieved within the timeout period, `False` is returned.

    Args:
    ------------
    video_url (str): The URL of the YouTube video from which the length is to be scraped.

    Returns:
    ------------
    Union[float, bool]: The length of the video in minutes as a float if successful; `False` if there is a timeout or
                         failure to retrieve the length.

    Raises:
    ------------
    TimeoutException: If the video length element does not become visible within the specified timeout period.
    """
    try:
        driver.get(video_url)

        video_length = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//div[@id='primary']//div[@class='ytp-time-display notranslate']//span[@class='ytp-time-duration']"
                )
            )
        )

        if isinstance(video_length, WebElement):
            unparsed_length = float(video_length.text.replace(":", "."))
            return unparsed_length

    except TimeoutException as e:
        print(f"TimeoutException: {e}")
        return False


def check_transcription(
        video_url: str
) -> bool:
    """
    Checks if the transcription feature is available for the given YouTube video.

    Description:
    ------------
    This function navigates to the provided YouTube video URL and verifies whether the transcription feature is available.
    It does this by checking if the transcription element is visible on the page after interacting with the description dropdown.

    Args:
    ------------
    video_url (str): The URL of the YouTube video to be checked for transcription availability.

    Returns:
    ------------
    bool: `True` if the transcription element is found and visible, `False` otherwise.

    Raises:
    ------------
    TimeoutException: If the expected elements do not become visible or clickable within the specified timeout period.
    """
    try:
        driver.get(video_url)

        # Wait until the main element is visible
        main_element = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//div[@id="columns"]//div[@class="style-scope ytd-watch-flexy"][1]//div[@id="below"]'
            ))
        )

        # Wait until the description element is clickable and then click it
        description_dropdown = WebDriverWait(main_element, 1).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@id="bottom-row"]'
            ))
        )
        description_dropdown.click()

        # Wait for the transcription element to become visible
        transcription_element = WebDriverWait(description_dropdown, 1).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[@slot='extra-content']//div[@id='items'][1]//div[@id='button-container']"
            ))
        )

        if isinstance(transcription_element, WebElement):
            print(transcription_element)
            return True

    except TimeoutException as e:
        print(f"TimeoutException: {e}")
        return False


def scrape_transcription(
        video_url: str
) -> Dict[str, str]:
    """
    Scrapes the transcription of a YouTube video from the provided URL.

    Description:
    ------------
    This function navigates to the given YouTube video URL and retrieves the video's transcription. It waits for various
    elements to become visible and interactable, such as the description dropdown and transcription button, to extract
    the transcription text along with its timestamps.

    Args:
    ------------
    video_url (str): The URL of the YouTube video from which the transcription is to be scraped.

    Returns:
    ------------
    Dict[str, str]: A dictionary where the keys are timestamps and the values are the corresponding transcription text.

    Raises:
    ------------
    TimeoutException: If any of the expected elements do not become visible or clickable within the specified timeout period.
    """

    try:
        driver.get(video_url)

        # Wait until the main element is visible
        main_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//div[@id="columns"]//div[@class="style-scope ytd-watch-flexy"][1]//div[@id="below"]'
            ))
        )

        # Wait until the description element is clickable and then click it
        description_dropdown = WebDriverWait(main_element, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@id="bottom-row"]'
            ))
        )
        description_dropdown.click()

        # Wait for the transcription element to become visible

        transcription_element = description_dropdown.find_element(
            By.XPATH,
            "//div[@slot='extra-content']//div[@id='items'][1]//div[@id='button-container']//div[@class='yt-spec-touch-feedback-shape__fill']"
        )

        transcription_element.click()
        time.sleep(2)

        transcription_bar = driver.find_element(
            By.XPATH,
            "//ytd-engagement-panel-section-list-renderer[@target-id='engagement-panel-searchable-transcript']"
        )

        timestamps = transcription_bar.find_elements(
            By.XPATH, '//div[@class="segment-timestamp style-scope ytd-transcript-segment-renderer"]'
        )
        transcription_texts = transcription_bar.find_elements(
            By.XPATH, '//yt-formatted-string[@class="segment-text style-scope ytd-transcript-segment-renderer"]'
        )

        full_transcription = {}
        for timestamp, transcription in zip(timestamps, transcription_texts):
            time_value = timestamp.text
            full_transcription[time_value] = transcription.text

        return full_transcription

    except TimeoutException as err:
        print(f"TimeoutException: {err}")


def scroll_down(engine: webdriver, scrolling_by: Tuple[int, int]):
    """
    Scrolls the webpage by a specified amount.

    Description:
    ------------
    This function uses JavaScript to scroll the webpage by the given horizontal and vertical pixel values. The
    `scrolling_by` tuple specifies the amount to scroll in the x and y directions, respectively.

    Args:
    ------------
    engine (webdriver): An instance of a Selenium WebDriver used to execute JavaScript on the webpage.
    scrolling_by (Tuple[int, int]): A tuple specifying the number of pixels to scroll horizontally (x) and vertically (y).

    Returns:
    ------------
    None
    """
    engine.execute_script(f"window.scrollBy{scrolling_by}")


def load_sys_prompt(
        prompt_name: str
) -> str:
    """
    Loads a system prompt from a YAML file based on the provided prompt name.

    Description:
    ------------
    This function reads the system prompts from a YAML file located at "helpers/prompts/system_prompts.yaml".
    It retrieves the prompt associated with the given `prompt_name` and returns its content.

    Args:
    ------------
    prompt_name (str): The name of the prompt to be loaded from the YAML file.

    Returns:
    ------------
    str: The content of the system prompt corresponding to the provided `prompt_name`.
    """
    with open("helpers/prompts/system_prompts.yaml", "r", encoding="utf-8") as prompt_file:
        system_prompts = yaml.safe_load(prompt_file)
    decoded_prompt = system_prompts[prompt_name]
    return decoded_prompt["sys_prompt"]


def chunk_up_text(
        document: str,
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 100
) -> List[str]:
    """
    Splits a document into smaller chunks based on the specified size and overlap.

    Description:
    ------------
    This function uses a `RecursiveCharacterTextSplitter` to divide a given document into chunks of a specified size,
    with optional overlap between consecutive chunks. The text is split based on the provided separators, and the
    resulting chunks are returned as a list of strings.

    Args:
    ------------
    document (str): The document to be split into chunks.
    chunk_size (Optional[int]): The maximum size of each chunk. Default is 1000 characters.
    chunk_overlap (Optional[int]): The number of overlapping characters between consecutive chunks. Default is 100 characters.

    Returns:
    ------------
    List[str]: A list of text chunks obtained by splitting the document.
    """
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators="\n\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunked_text = text_splitter.split_text(document)
    return chunked_text


def create_empty_vectorstore(
        embedding_model: Optional[Union[OpenAIEmbeddings, Any]] = text_embedding_v3_small
) -> FAISS:
    """
    Creates an empty FAISS vectorstore instance with the specified embedding model.

    Description:
    ------------
    This function initializes an empty FAISS vectorstore with the given embedding model. The vectorstore is created with
    an index that uses the L2 distance metric and an in-memory document store. The dimensions of the index are based on
    the embedding model's query embedding size.

    Args:
    ------------
    embedding_model (Optional[Union[OpenAIEmbeddings, Any]]): An optional embedding model used to determine the dimensions
                                                               of the vectorstore. If not provided, `text_embedding_v3_small`
                                                               is used by default.

    Returns:
    ------------
    FAISS: An empty FAISS vectorstore instance with the specified embedding model, ready to have documents added.
    """
    dimensions: int = len(embedding_model.embed_query("dummy"))
    empty_faiss_vs = FAISS(
        embedding_function=text_embedding_v3_small,
        index=IndexFlatL2(dimensions),
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
        normalize_L2=False
    )

    return empty_faiss_vs


def create_vectorstore_index(
        documents: Union[str, List[str]],
        vectorstore: FAISS,
) -> FAISS:
    """
    Creates or updates a vectorstore index with the provided documents.

    Description:
    ------------
    This function takes a list of documents or a single document string and adds them to the provided FAISS vectorstore index.
    The documents are converted into embeddings and added to the vectorstore. The updated vectorstore is then returned.

    Args:
    ------------
    documents (Union[str, List[str]]): A single document string or a list of document strings to be indexed.
    vectorstore (FAISS): An instance of the FAISS vectorstore to which the documents will be added.

    Returns:
    ------------
    FAISS: The updated FAISS vectorstore instance with the newly added documents.
    """

    document_list = Document(page_content=documents)
    _ = vectorstore.add_documents([document_list])  # returns a list of embedding ids

    return vectorstore


def search_timestamp(
        full_transcription: Dict[any, str],
        chat_message: str
) -> int:
    """
    Searches for the timestamp in a transcription that is most similar to a given chat message based on cosine similarity.

    Description:
    ------------
    This function calculates the similarity between the chat message and each transcript segment in the full transcription
    dictionary. It then identifies the timestamp of the segment that has the highest similarity score.

    Args:
    ------------
    full_transcription (Dict[any, str]): A dictionary where the keys are timestamps in "minutes:seconds" format and the values
                                         are the transcript segments associated with those timestamps.
    chat_message (str): The chat message whose similarity with the transcript segments is to be evaluated.

    Returns:
    ------------
    int: The timestamp (in seconds) of the transcript segment with the highest similarity score, rounded to the nearest second.
    """

    search_results = {}
    embedded_chat_message = text_embedding_v3_small.embed_query(chat_message)

    for timestamp, transcript in full_transcription.items():
        embedded_transcript = text_embedding_v3_small.embed_query(transcript)
        similarity_score = cosine_similarity([embedded_chat_message], [embedded_transcript])[0][0]
        search_results[f"{timestamp}"] = similarity_score

    sorted_values = sorted(search_results.items(), key=lambda item: item[1], reverse=True)
    timestamp, _ = sorted_values[0]

    minutes, seconds = map(int, timestamp.split(":"))
    total_seconds = minutes * 60 + seconds
    return round(total_seconds)


def take_screenshot(
        video_url: str
) -> Union[str, AnyStr, base64]:
    """
    Captures a screenshot of a video from the given URL and returns it as a base64 encoded string.

    Description:
    ------------
    This method navigates to the specified video URL, waits for the video element to become visible,
    scrolls the video element into view, and takes a screenshot of the video. The screenshot is then
    encoded in base64 format and returned as a string.

    Args:
    ------------
    video_url (str): The URL of the video from which the screenshot is to be taken.

    Returns:
    ------------
    str: A base64 encoded string representation of the screenshot image.

    Raises:
    ------------
    TimeoutException: If the video element does not become visible within the specified timeout period.
    """
    try:
        driver.get(video_url)
        video_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//video[@class='video-stream html5-main-video']"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", video_element)
        driver.save_screenshot('video_screenshot.png')

        with open("video_screenshot.png", "rb") as f:
            image = f.read()
            base64_image = base64.b64encode(image).decode('utf-8')

        return base64_image

    except TimeoutException as err:
        print(f"TimeoutException: {err}")
