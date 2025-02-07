import yaml

import streamlit as st
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI

from settings import secret_path
from langchain_tools import datetime_tool

with open(secret_path, "r", encoding="utf-8") as f:
    secret = yaml.safe_load(f)
api_key = secret["openai"]["api_key"]

llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0, streaming=True)
tools = load_tools(["ddg-search"]) + [datetime_tool]
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True)

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke({"input": prompt}, {"callbacks": [st_callback]})
        st.write(response["output"])
