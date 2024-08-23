from helpers.helper_functions import (
    check_application,
    check_transcription,
    load_sidebar_html
)
from streamlit_extras.stylable_container import stylable_container
import streamlit as st
import time
import asyncio

st.set_page_config(
    page_title="TalkYou - Talk With Videos!",
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon=":video_camera:"
)

with st.sidebar:
    sidebar_content = load_sidebar_html()
    st.html(sidebar_content)

