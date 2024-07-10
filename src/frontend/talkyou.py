import streamlit as st
import time
import asyncio
from helpers.helper_functions import check_application


st.set_page_config(
    page_title="TalkYou"
)

st.write("Check backend connection")
if st.button(
    label="Ping backend",
    key="pingKey"
):
    response = asyncio.run(check_application())
    if response is not None:
        st.success(response["status"])