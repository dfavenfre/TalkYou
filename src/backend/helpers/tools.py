from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from langchain.tools import BaseTool, StructuredTool, tool
from helpers.constants import service, options, driver
from helpers.helper_functions import (
    FetchTranscriptionModel,
    FetchVideoLengthModel,
    ScrapeTranscriptions
)

# Memory
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory
)

# Prompts
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate
)
from langchain_core.messages import AIMessage

# Output Parsers
from langchain_core.output_parsers import (
    JsonOutputParser,
    StrOutputParser,
    PydanticOutputParser
)

# Runnables
from langchain_core.runnables import (
    Runnable,
    RunnableMap,
    RunnableLambda,
    RunnablePassthrough
)
# Models
from langchain_openai import ChatOpenAI

# Tools
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import tool
from langchain.tools import BaseTool, StructuredTool, tool

# Fundamentals
from helpers.constants import service, options, driver
from langchain_core.tracers.context import tracing_v2_enabled
from typing import List, Optional, Tuple, Any, Dict, Sequence, Type, Union
from pydantic import BaseModel, Field
from operator import itemgetter
import langchain_community
from datetime import datetime
from dotenv import load_dotenv
import time
import asyncio
import sqlite3
import yaml
import os

load_dotenv()


class TranscriptionTool(BaseTool):
    name: str = "CheckTranscriptionElement"
    description: str = "Checks whether YT video has a transcription button or not"
    arg_schema: Type[BaseModel] = FetchTranscriptionModel

    def _run(
            self,
            video_url: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> bool:
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
            transcription_element = WebDriverWait(description_dropdown, 5).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//div[@slot='extra-content']//div[@id='items'][1]//div[@id='button-container']"
                ))
            )

            if isinstance(transcription_element, WebElement):
                return True

        except TimeoutException as e:
            print(f"TimeoutException: {e}")
            return False


class VideoLengthTool(BaseTool):
    name: str = "CheckVideoLength"
    description: str = "Checks the length of the YT video"
    arg_schema: Type[BaseModel] = FetchVideoLengthModel

    def _run(
            self,
            video_url: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Union[float, int]:
        try:
            driver.get(video_url)

            video_length = WebDriverWait(driver, 3).until(
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


class TranscriptionScrapperTool(BaseTool):
    name: str = "TranscriptionScrapper"
    description: str = "Scrapes transcriptions from YT videos"
    args_schema: Type[BaseModel] = ScrapeTranscriptions

    def _run(
            self,
            video_url: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, str]:
        try:

            driver.get(video_url)

            main_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//div[@id="columns"]//div[@class="style-scope ytd-watch-flexy"][1]//div[@id="below"]'
                ))
            )

            description_dropdown = WebDriverWait(main_element, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//div[@id="bottom-row"]'
                ))
            )
            description_dropdown.click()

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


transcription_checker = TranscriptionTool()
video_length_checker = VideoLengthTool()
transcription_scrapper = TranscriptionScrapperTool()
