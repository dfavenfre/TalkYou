import streamlit as st
import time
import asyncio
from helpers.helper_functions import check_application, check_transcription

st.set_page_config(
    page_title="TalkYou"
)

with st.container(border=True, height=400):
    col1, col2 = st.columns([0.5, 0.5], gap="small")
    with col1:
        st.write("Check backend connection")
        if st.button(
                label="Ping backend",
                key="pingKey"
        ):
            response = asyncio.run(check_application())
            if response is not None:
                st.success(response["status"])

    with col2:
        st.write("Check Video Transcription")
        video_url = st.text_input(label="Add Video URL")
        if st.button(
                label="Check Transcription",
                key="transcriptionKey"
        ):
            if len(video_url) >= 10:
                video_transcription = asyncio.run(check_transcription(video_url))
                if video_transcription:
                    st.write(video_transcription)
                    st.success("Found Transcription")
                else:
                    st.write(video_transcription)
                    st.error(f"No Transcription found")
            elif len(video_url) < 10:
                st.warning("Please add a video URL before proceeding")
