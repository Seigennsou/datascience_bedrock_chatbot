import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from time import sleep
from uipages import navigate

if 'cookies' not in st.session_state:
    cookies = EncryptedCookieManager(
                prefix="mychatbot_", 
                password="supersecretss" 
    )
    while not cookies.ready():
        st.write("loding...")
        sleep(1)
    st.session_state['cookies'] = cookies


def main():

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "Login"
    if 'logged_in_until' not in st.session_state:
        st.session_state['logged_in_until'] = None


    navigate.navigate()

if __name__ == "__main__":
    main()
