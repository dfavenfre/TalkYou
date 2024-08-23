from helpers.constants import (
    backend_signal_url,
    agent_url
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


def check_application():
    try:
        response = requests.get(
            url=backend_signal_url,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()

    except Exception as e:
        st.warning(f"Error While Checking Backend Connection: {e}")


def check_transcription(payload: str):
    package = {"video_url": payload}
    try:
        response = requests.post(
            url=agent_url,
            headers={"Content-Type": "application/json"},
            json=package
        )
        if response is not None:
            data = response.json()
            return data

    except Exception as err:
        st.warning(f"Error While Checking Transcription: {err}")


def load_sidebar_html() -> str:
    """
    Description:
    -----------
    Function to load the sidebar HTML template, read CSS, and insert dynamic content.

    Args:
    -----------


    Returns:
    -----------
    The resulting HTML string with embedded CSS.
    """

    with open("helpers/elements/sidebar.css", 'r', encoding='utf-8') as css_file:
        css_content = f"<style>{css_file.read()}</style>"

    with open("helpers/elements/sidebar_element.html", 'r', encoding='utf-8') as html_file:
        html_template = html_file.read()

    final_html = f"{css_content}\n{html_template}"

    return final_html
