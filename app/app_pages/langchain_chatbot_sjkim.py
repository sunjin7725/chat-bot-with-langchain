import uuid
import yaml
from datetime import datetime

import streamlit as st
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_tools import datetime_tool, ddg_search, who_are_you_tool, get_remote_ip_tool, get_remote_ip
from streamlit_utils import display_chat_history

from settings import secret_path
from database.client import PostgresClient
from database.utils import get_chat_history, delete_chat_hitory

PAGE_USER = "sjkim"
st.session_state.clear()

with open(secret_path, "r", encoding="utf-8") as f:
    secret = yaml.safe_load(f)
api_key = secret["openai"]["api_key"]

llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0, streaming=True)
tools = [datetime_tool, ddg_search, who_are_you_tool, get_remote_ip_tool]

prompt = ChatPromptTemplate(
    [
        (
            "system",
            """
            Assistant can assist with a variety of tasks, from answering simple questions to providing detailed explanations.

            Assistant has access to the following tools:
            {tools}

            Please respond in the following 3 formats:

            1. If a tool is needed:
            ```
            Thought: Do I need to use a tool? Yes
            Action: [the tool to use: {tool_names}]
            Action Input: [input for the tool]
            Observation: [result from the tool]
            ```

            2. If no tool is needed:
            ```
            Thought: Do I need to use a tool? No
            Final Answer: [your response here]
            ```

            3. If the assistant doesn't know any information to respond to the user:
            ```
            Thought: Do I need to use a tool? No
            Final Answer: [your response here]
            ```

            If you respond with 'Final Answer', please provide your response in the user's language.

            Previous conversation history:
            {chat_history}

            New input: {input}
            {agent_scratchpad}
            """,
        )
    ]
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "client" not in st.session_state:
    st.session_state.client = PostgresClient()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = get_chat_history(PAGE_USER, st.session_state.client)

if "memory" not in st.session_state:
    chat_memory = InMemoryChatMessageHistory()
    if st.session_state.chat_history:
        for history in st.session_state.chat_history:
            if history.get("role") == "user":
                chat_memory.add_user_message(history.get("content"))
            else:
                chat_memory.add_ai_message(history.get("content"))

    st.session_state.memory = ConversationBufferWindowMemory(
        chat_memory=chat_memory, return_messages=True, memory_key="chat_history", input_key="input", k=10
    )

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=st.session_state.memory, verbose=True)

display_chat_history(st.session_state.chat_history)

if prompt := st.chat_input():
    with st.chat_message("user"):
        st.write(prompt)

        history = {
            "session_id": st.session_state.session_id,
            "username": PAGE_USER,
            "ip": get_remote_ip(),
            "role": "user",
            "content": prompt,
            "create_datetime": datetime.now(),
        }
        st.session_state.chat_history.append(history)
        st.session_state.client.insert("chat", history)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke({"input": prompt}, {"callbacks": [st_callback]})

        # 응답 형식 검증
        if isinstance(response, dict) and "output" in response:
            st.write(response["output"])

            history = {
                "session_id": st.session_state.session_id,
                "username": PAGE_USER,
                "ip": get_remote_ip(),
                "role": "assistant",
                "content": response["output"],
                "create_datetime": datetime.now(),
            }
            st.session_state.chat_history.append(history)
            st.session_state.client.insert("chat", history)
        else:
            st.write(
                "Error: The response format is incorrect. Please ensure the response follows the specified format."
            )
            print("Invalid response format:", response)  # 디버깅을 위한 출력


def delete_history():
    delete_chat_hitory(PAGE_USER, st.session_state.client)
    st.session_state.chat_history = get_chat_history(PAGE_USER, st.session_state.client)
    st.session_state.memory = ConversationBufferWindowMemory(
        return_messages=True, memory_key="chat_history", input_key="input", k=10
    )
    display_chat_history(st.session_state.chat_history)


st.button("Delete History", on_click=delete_history)
