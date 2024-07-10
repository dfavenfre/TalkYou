from typing import (
    Optional,
    Union,
    Dict,
    Any
)
import streamlit as st
import requests
import time


backend_signal_url = "http://backend:8000/backend_check"


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
