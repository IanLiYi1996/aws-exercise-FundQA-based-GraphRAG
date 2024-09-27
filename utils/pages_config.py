import streamlit as st
import streamlit_authenticator as stauth
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
import yaml
from yaml.loader import SafeLoader


def get_authenticator():
    with open('config_files/stauth_config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        float(config['cookie']['expiry_days']),
        config['pre-authorized']
    )


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar():
    with st.sidebar:
        if st.session_state.get('authentication_status'):
            st.page_link("pages/chat.py", label="chat", icon="🌍")
            if st.button("Log out"):
                logout()


def logout():
    authenticator = get_authenticator()
    authenticator.logout('Logout', 'unrendered')
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("main.py")
