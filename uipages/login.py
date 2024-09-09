import streamlit as st
from datetime import datetime, timedelta
import json
from time import sleep

    
def load_user_data():
    with open('data/users.json', 'r') as file:
        return json.load(file)

def get_user_credentials(username):
    users = load_user_data()['users']
    for user in users:
        if user['username'] == username:
            return user
    return None

def login():
    cookies = st.session_state['cookies']
    if cookies.get("logged_in") == "True" and not st.session_state['logged_in']:
        st.session_state['logged_in'] = True
        st.session_state['username'] = cookies.get("username")
        expires_at_timestamp = cookies.get("expires_at")
        if expires_at_timestamp:
            st.session_state['logged_in_until'] = datetime.fromtimestamp(float(expires_at_timestamp))
        st.session_state['current_page'] = "chatbot"
        st.rerun()

        
    else:
        st.title("Login")
        with st.form(key="login_form"):
            username = st.text_input("Username",value="admin")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                with st.spinner("Logging in..."):
                    user = get_user_credentials(username)
                    if user and user['password'] == password:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['logged_in_until'] = datetime.now() + timedelta(minutes=60)
                        st.session_state['current_page'] = "chatbot"
                        cookies["logged_in"] = "True"
                        cookies["username"] = username
                        cookies["expires_at"] = str(st.session_state['logged_in_until'].timestamp()) 
                        cookies.save()
                        st.session_state['cookies'] = cookies
                        placeholder = st.empty()
                        with placeholder.container():
                            st.write("")  
                        sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                    
        

def logout():
    cookies = st.session_state['cookies']
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.session_state['logged_in_until'] = None
    st.session_state['current_page'] = "Login"
    cookies["logged_in"] = "False"
    cookies["username"] = ""
    cookies["expires_at"] = ""
    cookies.save()
    st.session_state['cookies'] = cookies
    st.rerun()


