import streamlit as st
from uipages import login
from uipages import chatbot


def navigate():
    if st.session_state['current_page'] == "Login":
        login.login()        
    elif st.session_state['current_page'] == "chatbot":
        chatbot.chatbot()
    elif st.session_state['current_page'] == None:
        st.write("Please select a page to navigate")