import asyncio
import base64
from pathlib import Path

import httpx
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
from jinja2 import Template
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


async def chat_bot(
        video_url: str,
        chat_message: Optional[str] = None,
) -> Union[Any, str, Dict[str, Any]]:
    try:
        form_data = {
            "video_url": video_url,
            "chat_message": chat_message
        }

        response = requests.post(
            url=agent_url,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response is not None:
            return response.json()

    except Exception as err:
        st.warning(f"Error While Chat Bot: {err}")


def submit_video_url(video_url: str) -> None:
    if "youtube" not in video_url:
        place_holder = st.empty()
        st.warning("Please make sure that you send a YouTube video URL")
        time.sleep(2)
        place_holder.empty()

    else:
        place_holder = st.empty()
        with st.spinner('Preparing The Chatbot...'):
            response = asyncio.run(chat_bot(video_url))
            if response:
                place_holder.success("Vectorstore Created, Ready To Chat !")
            time.sleep(2)
            place_holder.empty()
            st.session_state.video_url = video_url
        st.rerun()


def load_sidebar_html() -> str:
    """
    Description:
    -----------
    Function to load the sidebar HTML template, read CSS, and insert dynamic content.

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


def render_chat():
    # Uncomment the below assignment when needed
    # if "last_rendered_index" not in st.session_state:
    #     st.session_state["last_rendered_index"] = 0

    with open("helpers/elements/chat_template.html", 'r', encoding='utf-8') as html_file:
        html_template = html_file.read()

    with open("helpers/elements/chat_styles.css", 'r', encoding='utf-8') as css_file:
        css_content = f"<style>{css_file.read()}</style>"

    final_html = f"{css_content}\n{html_template}"

    new_messages = st.session_state.messages[st.session_state["last_rendered_index"]:]
    st.session_state["last_rendered_index"] = len(st.session_state.messages)

    template = Template(final_html)
    rendered_html = template.render(messages=new_messages)

    st.html(rendered_html)


def stream_text(text: str) -> str:
    for chunk in text.split():
        yield chunk + " "
        time.sleep(0.05)


def render_landing_page() -> None:
    with open("helpers/elements/landing_page_content.html", 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()

    with open("helpers/elements/landing_page_styles.css", 'r', encoding='utf-8') as css_file:
        css_content = f"<style>{css_file.read()}</style>"

    full_html = f"{css_content}\n{html_content}"
    st.html(full_html)
