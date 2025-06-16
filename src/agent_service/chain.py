import logging
from typing import Dict, List

from langchain.retrievers.merger_retriever import MergerRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough

from agent_service.llm import get_llm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_rag_chain(retrievers: List[BaseRetriever]) -> Runnable:
    """
    Creates the main Retrieval-Augmented Generation (RAG) chain.

    Args:
        retrievers: A list of retriever instances to combine.

    Returns:
        A runnable chain that takes a question and returns an answer.
    """
    logging.info("Creating RAG chain with MergerRetriever...")

    merger = MergerRetriever(retrievers=retrievers)

    template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)

    llm = get_llm(temperature=0, streaming=False)

    rag_chain = (
        {"context": merger, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logging.info("RAG chain created successfully.")

    return rag_chain
