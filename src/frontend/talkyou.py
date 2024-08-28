import base64

from helpers.helper_functions import (
    load_sidebar_html,
    render_chat,
    chat_bot,
    submit_video_url
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

if "last_rendered_index" not in st.session_state:
    st.session_state["last_rendered_index"] = 0

with st.sidebar:
    sidebar_content = load_sidebar_html()
    st.html(sidebar_content)

if st.session_state["video_url"] is None:
    st.image("helpers/elements/assets/talkyou-langgraph-schema.jpg")
    with st.expander(label="Welcome To TalkYou 👋", expanded=True):
        video_url = st.text_input("Have any videos on your mind?")
        if st.button(
                label="Submit",
                key="videoUrlSubmission",
        ):
            submit_video_url(video_url)

elif st.session_state.video_url is not None:

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Welcome, It's Your Video Talking! What do you like to ask me?"}
        ]
    render_chat()

    if user_message := st.chat_input(
            placeholder="What do you like to ask me?",
            key="chat_input_message",
            max_chars=250
    ):

        st.session_state.messages.append({"role": "user", "content": user_message})
        render_chat()

        ai_message = asyncio.run(
            chat_bot(
                video_url=st.session_state.video_url,
                chat_message=user_message
            )
        )

        if "screenshot_base64" in ai_message.keys() and ai_message["identified_request"] == "image":
            converted_image = base64.b64decode(ai_message["screenshot_base64"])
            st.image(converted_image)

        else:
            st.session_state.messages.append({"role": "assistant", "content": ai_message["response"]})
            render_chat()
