from typing import Optional, List, Dict, Tuple, Union, Any, AnyStr
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate
)
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
from io import BytesIO
import time
import requests
import os
import io
import yaml
import base64
import json


def load_sys_prompt(
        prompt_name: str
) -> str:
    with open("helpers/prompts/system_prompts.yaml", "r", encoding="utf-8") as prompt_file:
        system_prompts = yaml.safe_load(prompt_file)
    decoded_prompt = system_prompts[prompt_name]
    return decoded_prompt["sys_prompt"]
