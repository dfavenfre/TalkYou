from langchain_core.agents import AgentAction, AgentFinish
from langgraph.graph import StateGraph, START, END, MessagesState
from typing import (
    TypedDict,
    Union,
    Tuple,
    Dict,
    List
)
from helpers.constants import memory
from helpers.agent_states import (
    GraphState,
    check_video_length,
    check_transcription_element,
    download_with_pytube,
    extract_transcription,
    init_vectorstore,
    selenium_or_pytube,
    scrape_or_download,
    load_vectorstore_states,
    check_vectorstore_presence,
    query_identifier,
    check_request_type,
    proceed_to_rag,
    proceed_to_image_retrieval,
    take_video_screenshot
)

workflow = StateGraph(GraphState)
workflow.add_node("check_vectorstore_presence", load_vectorstore_states)
workflow.add_node("query_identifier", query_identifier)
workflow.add_node("continue_rag", proceed_to_rag)
workflow.add_node("continue_image_retrieval", proceed_to_image_retrieval)
workflow.add_node("check_video_length", check_video_length)
workflow.add_node("check_transcription", check_transcription_element)
workflow.add_node("download_with_pytube", download_with_pytube)
workflow.add_node("extract_transcription", extract_transcription)
workflow.add_node("create_vectorstore", init_vectorstore)
workflow.add_node("take_screenshot", take_video_screenshot)

workflow.add_edge(START, "check_vectorstore_presence")
workflow.add_conditional_edges(
    "check_vectorstore_presence",
    check_vectorstore_presence,
    {
        "Chatbot": "query_identifier",
        "Fetch Data": "check_video_length"
    }
)

workflow.add_conditional_edges(
    "query_identifier",
    check_request_type,
    {
        "Information": "continue_rag",
        "Image": "continue_image_retrieval",
    }
)

workflow.add_edge("continue_rag", END)
workflow.add_edge("continue_image_retrieval", "take_screenshot")
workflow.add_edge("take_screenshot", END)

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
workflow.add_edge("download_with_pytube", "create_vectorstore")
workflow.add_edge("extract_transcription", "create_vectorstore")
workflow.add_edge("create_vectorstore", END)

chatbot = workflow.compile(checkpointer=memory)
