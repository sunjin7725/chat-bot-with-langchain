"""
This module provides utility functions for Streamlit applications.

It includes functions for displaying chat history and getting user input.
"""

import streamlit as st


def display_chat_history(chat_history):
    """
    Displays the chat history in the Streamlit app.

    Args:
        chat_history (list): The list of chat messages to display.
    """
    for content in chat_history:
        with st.chat_message(content["role"]):
            st.markdown(content["content"])


def talk(text, role, history):
    """
    Displays a message in the Streamlit app and updates the chat history.

    Args:
        text (str): The message text to display.
        role (str): The role of the speaker (e.g., 'user' or 'assistant').
        history (list): The chat history to update with the new message.
    """
    st.markdown(text)
    history.append({"role": role, "content": text})
