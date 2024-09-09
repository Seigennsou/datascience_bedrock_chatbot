import streamlit as st
from uipages import login
from chatbot.chat import ChatInterfaceStreaming
from chatbot.sidebar import sidebar
from agents.data_sc import ciginfo
from bedrock.bedrock_client import BedrockClient

def chatbot():
    st.sidebar.write(f"Logged in as {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        login.logout()

    cig = ciginfo()
    cig = sidebar(cig)
    bedrock_client = BedrockClient(cig.region)

    chat_interface = ChatInterfaceStreaming(bedrock_client, cig)
    chat_interface.run()

