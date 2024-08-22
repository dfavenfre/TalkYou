from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
import yaml

load_dotenv()


# Functions
def load_sys_prompt(
        prompt_name: str
) -> str:
    with open("helpers/prompts/system_prompts.yaml", "r", encoding="utf-8") as prompt_file:
        system_prompts = yaml.safe_load(prompt_file)
    decoded_prompt = system_prompts[prompt_name]
    return decoded_prompt["sys_prompt"]


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

text_embedding_v3_small = OpenAIEmbeddings(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    model="text-embedding-3-small"
)

# LANGGRAPH MEMORY
memory = MemorySaver()

# LANGGRAPH THREAD
selected_thread = {"configurable": {"thread_id": "1"}}

# PROMPTS
request_identification_prompt_template = load_sys_prompt("request_identification")
rag_prompt_template = load_sys_prompt("rag_tool")
