from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

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
        max_length=150,
    )

    class Config:
        schema_extra = {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=2hT9_QrEhb0"
            }
        }


def check_transcription(
        video_url: Union[str, AnyStr]
) -> WebElement | bool:
    """
    Description:
    Checks if there is 'transcription' element in the provided video URL.

    :param video_url: URL of the video you want to check.
    :return: True if there is 'transcription' element in the provided video URL.
    """
    try:
        driver.get(video_url)

        # Wait until the main element is visible
        main_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//div[@id="columns"]//div[@class="style-scope ytd-watch-flexy"][1]//div[@id="below"]'
            ))
        )
        scroll_down(driver, (0, 100))

        # Wait until the description element is clickable and then click it
        WebDriverWait(main_element, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@id="bottom-row"]'
            ))
        ).click()

        time.sleep(2)
        # Scroll down to load more content if necessary
        scroll_down(driver, (100, 650))

        # Wait for the transcription element to become visible
        transcription_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR, 'div#columns div.style-scope.ytd-watch-flexy > div#below'
                )
            )
        )

        if transcription_element is not None:
            driver.save_screenshot('backend_screenshot.png')
            return transcription_element

        else:
            driver.save_screenshot('backend_screenshot.png')
            return False

    except Exception as err:
        print(f"An error occurred: {err}")
        return False

    finally:
        driver.quit()


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
    with open("helpers/prompts/system_prompts.yaml", "r", encoding="utf-8") as prompt_file:
        system_prompts = yaml.safe_load(prompt_file)
    decoded_prompt = system_prompts[prompt_name]
    return decoded_prompt["sys_prompt"]


if __name__ == "__main__":
    found_transcript, transcription_button = check_transcription("https://www.youtube.com/watch?v=2hT9_QrEhb0")
    if found_transcript:
        print(f"Found The Transcription Element --> {transcription_button}")
