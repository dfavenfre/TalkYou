from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

from helpers.constants import service, options, driver
from typing import (Optional, List, Dict, Tuple, Union, Any, AnyStr)
from langchain_core.prompts import (ChatPromptTemplate, PromptTemplate)
from langchain_openai import ChatOpenAI
from pydantic import (BaseModel, Field, HttpUrl)
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import time
import requests
import os
import io
import yaml
import base64
import json


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

# if __name__ == "__main__":
#     found_transcript = check_transcription("https://www.youtube.com/watch?v=bG4VYwFnU8k&t=5s")
#     if found_transcript:
#         print(f"Found The Transcription Element")
#     else:
#         print(f"Not Found The Transcription Element")
