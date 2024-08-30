from helpers.helper_functions import (
    load_sidebar_html,
    chat_bot,
    submit_video_url,
    render_landing_page
)
import streamlit as st
import asyncio
import base64

st.set_page_config(
    page_title="TalkYou - Talk With Videos!",
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon=":video_camera:"
)

# SESSION STATES
if "video_url" not in st.session_state:
    st.session_state["video_url"] = None

with st.sidebar:
    sidebar_content = load_sidebar_html()
    st.html(sidebar_content)

if st.session_state["video_url"] is None:
    render_landing_page()
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
            {
                "role": "assistant",
                "content": "Welcome, It's Your Video Talking! What do you like to ask me?"
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_message := st.chat_input(
            placeholder="What do you like to ask me?",
            key="chat_input_message",
            max_chars=250
    ):

        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.write(user_message)

        with st.spinner("Looking for an answer..."):
            ai_message = asyncio.run(
                chat_bot(
                    video_url=st.session_state.video_url,
                    chat_message=user_message
                )
            )

            if "screenshot_base64" in ai_message.keys() and ai_message["identified_request"] == "image":
                converted_image = base64.b64decode(ai_message["screenshot_base64"])
                with st.chat_message("assistant"):
                    st.image(converted_image)

            else:
                st.session_state.messages.append({"role": "assistant", "content": ai_message["response"]})
                with st.chat_message("assistant"):
                    st.write(ai_message["response"])
