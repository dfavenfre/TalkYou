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
from typing import Optional, Dict, Tuple, Union, Any, List
from pydantic import BaseModel, Field
from langchain_community.docstore.in_memory import InMemoryDocstore
from sklearn.metrics.pairwise import cosine_similarity
from faiss import IndexFlatL2
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import yaml
import base64


class RagToolModel(BaseModel):
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
    request_category: str = Field(
        description="Category of the request, which is either 'information' or 'image'",
    )


class ScrapeTranscriptions(BaseModel):
    video_url: str = Field(
        description="URL of the video that you want to scrape the transcription of",
        min_length=10,
        max_length=100,
    )


class FetchTranscriptionModel(BaseModel):
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


def scrape_video_length(url):
    try:
        driver.get(url)

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

    # finally:
    #     driver.close()


def check_transcription(video_url: str) -> bool:
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

    # finally:
    #     driver.close()


def scrape_transcription(video_url: str) -> Dict[str, str]:
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

    # finally:
    #     driver.close()


def scroll_down(engine: webdriver, scrolling_by: Tuple[int, int]):
    """
    Description:
    Scroll down to bottom of the page.

    :engine: webdriver object
    :scrolling_by: the amount of scrolling (pixel)
    """
    engine.execute_script(f"window.scrollBy{scrolling_by}")


def load_sys_prompt(
        prompt_name: str
) -> str:
    with open("elements/prompts/system_prompts.yaml", "r", encoding="utf-8") as prompt_file:
        system_prompts = yaml.safe_load(prompt_file)
    decoded_prompt = system_prompts[prompt_name]
    return decoded_prompt["sys_prompt"]


def chunk_up_text(
        document: str,
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 100
):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators="\n\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunked_text = text_splitter.split_text(document)
    return chunked_text


def create_empty_vectorstore(
        embedding_model: Optional[Union[OpenAIEmbeddings, Any]] = text_embedding_v3_small
):
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
    document_list = Document(page_content=documents)
    _ = vectorstore.add_documents([document_list])  # returns a list of embedding ids

    return vectorstore


def search_timestamp(
        full_transcription: Dict[any, str],
        chat_message: str
) -> int:
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


def take_screenshot(video_url: str) -> any:
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

    finally:
        driver.close()
