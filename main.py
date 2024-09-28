import time

import streamlit as st
from utils.pages_config import get_authenticator

st.set_page_config(
    page_title="FundQA-by-GraphRag ChatBot",
    page_icon="👋",
)

authenticator = get_authenticator()
name, authentication_status, username = authenticator.login('main')

if st.session_state['authentication_status']:
    time.sleep(0.5)
    st.session_state['auth_name'] = name
    st.session_state['auth_username'] = username
    st.switch_page("pages/chat.py")
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')


## test code:streamlit run main.py --server.enableStaticServing false --logger.level info —-client.toobarMode viewer --client.showErrorDetails false --browser.gatherUsageStats false —-theme.base light