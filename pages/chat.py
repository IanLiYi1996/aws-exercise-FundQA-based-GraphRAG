
import streamlit as st
import pandas as pd
import plotly.express as px

from core.chat_service import ChatService
from utils.pages_config import make_sidebar

from dotenv import load_dotenv


def history_show():
    for item in st.session_state.messages:
        if item["role"] == "user":
            with st.chat_message("user"):
                st.write(item["content"])
        else:
            with st.chat_message("assistant"):
                st.write(item["content"])

def clean_st_history(selected_profile):
    st.session_state.messages = []

def main():
    load_dotenv()

    st.set_page_config(page_title="Demo", layout="wide")
    make_sidebar()

    st.subheader('FundQA ChatBot Example')

    with st.sidebar:
        st.title('Setting')
        clean_history = st.button("clean history", on_click=clean_st_history)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    history_show()

    text_placeholder = "Type your query here..."

    search_box = st.chat_input(placeholder=text_placeholder)

    if search_box != "Type your query here...":
        if search_box is not None and len(search_box) > 0:
            with st.chat_message("user"):
                st.session_state.messages.append(
                    {"role": "user", "content": search_box, "type": "text"})
                st.write(search_box)
            # 调用 ChatService
            chat_service = ChatService()
            response = chat_service.execute_chat(search_box)
            with st.chat_message("assistant"):
                st.write(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response, "type": "text"})


if __name__ == '__main__':
    main()