from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from helpers.constants import service, options, driver, text_embedding_v3_small
from typing import Optional, Dict, Tuple, Union, Any, List
from pydantic import BaseModel, Field
from langchain_community.docstore.in_memory import InMemoryDocstore
from faiss import IndexFlatL2
import time
import yaml


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

    finally:
        driver.close()


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

    finally:
        driver.close()


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

    finally:
        driver.close()


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
        embedding_model: Optional[Union[OpenAIEmbeddings, Any]] = text_embedding_v3_small,
        vectorstore_name: Optional[str] = "empty_faiss_vs"
):
    dimensions: int = len(embedding_model.embed_query("dummy"))
    empty_faiss_vs = FAISS(
        embedding_function=text_embedding_v3_small,
        index=IndexFlatL2(dimensions),
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
        normalize_L2=False
    )

    empty_faiss_vs.save_local(vectorstore_name)

    return empty_faiss_vs


def create_vectorstore_index(
        documents: Union[str, List[str]],
        vectorstore: FAISS,
) -> FAISS:
    _ = vectorstore.add_texts(documents)  # returns a list of embedding ids

    return vectorstore

# if __name__ == "__main__":
#     import pandas as pd
#
#     transcription_dictionary = scrape_transcription("https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s")
#     if transcription_dictionary is not None:
#         transcription_data = pd.DataFrame(
#             {
#                 "timestamp": transcription_dictionary.keys(),
#                 "transcription": transcription_dictionary.values()
#             }
#         )
#         print(transcription_data.head())
#         transcription_data.to_csv("transcription_data.csv", index=False)
#     else:
#         print(f"Not Found The Transcription Element")
