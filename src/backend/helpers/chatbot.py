from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import (
    TypedDict,
    Union,
    Tuple,
    Dict,
    List
)
import asyncio
from helpers.agent_states import (
    GraphState,
    check_video_length,
    check_transcription_element,
    download_with_pytube,
    extract_transcription,
    create_vectorstore,
    selenium_or_pytube,
    scrape_or_download
)

workflow = StateGraph(GraphState)

workflow.add_node("check_video_length", check_video_length)
workflow.add_node("check_transcription", check_transcription_element)
workflow.add_node("download_with_pytube", download_with_pytube)
workflow.add_node("extract_transcription", extract_transcription)
workflow.add_node("create_vectorstore", create_vectorstore)

workflow.add_edge(START, "check_video_length")
workflow.add_conditional_edges(
    "check_video_length",
    selenium_or_pytube,
    {
        "Selenium": "check_transcription",
        "Pytube": "download_with_pytube"
    }
)

workflow.add_conditional_edges(
    "check_transcription",
    scrape_or_download,
    {
        "Scrape": "extract_transcription",
        "Download": "download_with_pytube"
    }
)

workflow.add_edge("extract_transcription", "create_vectorstore")
workflow.add_edge("create_vectorstore", END)

chatbot = workflow.compile()
