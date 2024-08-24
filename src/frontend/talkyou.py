from helpers.helper_functions import (
    check_application,
    check_transcription,
    load_sidebar_html,
    render_chat
)
from streamlit_extras.stylable_container import stylable_container
import extra_streamlit_components as esc
import streamlit as st
import time
import asyncio

st.set_page_config(
    page_title="TalkYou - Talk With Videos!",
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon=":video_camera:"
)

# SESSION STATES
if "video_url" not in st.session_state:
    st.session_state["video_url"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []


with st.sidebar:
    sidebar_content = load_sidebar_html()
    st.html(sidebar_content)

if st.session_state["video_url"] is None:
    with st.popover("Insert video url here", use_container_width=True):
        st.markdown("Hello 👋")
        video_url = st.text_input("Have any videos on your mind?")
        if "youtube" not in video_url:
            place_holder = st.empty()
            st.warning("Please make sure that you send a YouTube video URL")
            time.sleep(2)
            place_holder.empty()
        else:
            st.session_state["video_url"] = video_url
            st.rerun()


elif st.session_state.video_url is not None:

    render_chat(st.session_state.messages)

    if user_message := st.chat_input(
            placeholder="What do you like to ask me?",
            key="chat_input_message",
            max_chars=250
    ):
        # Append the new user message
        st.session_state.messages.append({"role": "user", "content": user_message})

        # Generate a response (in this example, a static response)
        _demo: str = "this is a test assistant message"
        st.session_state.messages.append({"role": "assistant", "content": _demo})

        # Re-render the chat to include the new messages
        render_chat(st.session_state.messages)

