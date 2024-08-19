from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# SELENIUM
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.99 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)

# MODELS
gpt_4o_mini = ChatOpenAI(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=1e-10,
    max_tokens=1000,
    model_name="gpt-4o-mini"
)

gpt_3_5 = ChatOpenAI(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=1e-10,
    max_tokens=1000,
    model_name="gpt-3.5-turbo"
)
