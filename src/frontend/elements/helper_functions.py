from elements.constants import (
    backend_signal_url,
    fetch_transcription_element
)
from typing import (
    Optional,
    Union,
    Dict,
    Any
)
import streamlit as st
import requests
import time


async def check_application():
    try:
        response = requests.get(
            url=backend_signal_url,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()

    except Exception as e:
        st.warning(f"Error While Checking Backend Connection: {e}")


async def check_transcription(payload: str):
    package = {"video_url": payload}
    try:
        response = requests.post(
            url=fetch_transcription_element,
            headers={"Content-Type": "application/json"},
            json=package
        )
        if response is not None:
            data = response.json()
            return data

    except Exception as err:
        st.warning(f"Error While Checking Transcription: {err}")
