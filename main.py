import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import numpy as np
import pandas as pd                                 
import plotly.express as px                         
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from deta import Deta
import time
import datetime
import calendar
import json
from collections import Counter

st.set_page_config('User Dashboard', ':file_folder:', layout='wide')         # https://www.webfx.com/tools/emoji-cheat-sheet/
st.title(':file_folder:' + " " + 'User Dashboard')

# Settings For Job Sheet Database
dat = ['dat']
cli = ['cli']
add = ['add']
cat = ['cat']
des = ['des']
pay = ['Fees']

# Job Sheet Database Interface
DETA_KEY = 'c0jo61nr_19VVPZAnQBZPws1WGgaU2HDCW1kyth28'
deta = Deta(DETA_KEY)
db = deta.Base('job_sheet')

def insert_date(dat, cli, add, cat, des, pay):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db.put({'date': dat, 'client': cli, 'address': add, 'category': cat, 'description': des,'payment': pay})

def fetch_all_dates():
    """Returns a dict of all date"""
    res = db.fetch()
    return res.items

# User Password Database
DETA_KEY_1 = "c0jo61nr_P1wSYy8XFqjnwgyeWUXqU635PWYK4A85"
deta_1 = Deta(DETA_KEY_1)                           # Initialize with a project key
db_1 = deta_1.Base("users_db")                      # This is how to create/connect a database

def fetch_all_users():
    """Returns a dict of all users"""
    res = db_1.fetch()
    return res.items

# User Authentication
users = fetch_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "user_dashboard", "abcdef", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    #st.subheader(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")
    st.sidebar.subheader(f"User ID: {username}")
    st.sidebar.subheader(f"User Name: {name}")

    selected = option_menu(menu_title = None, options = ['Dashboard','Job Sheet'], orientation='horizontal')

    if selected == 'Dashboard':
        st.subheader('Job Sheet Summary:')
        df = fetch_all_dates()
        df = json.dumps(df)
        df = pd.read_json(df)
        fees = df['payment'].map(Counter).groupby(df['key']).sum()
        fees = df['payment'].apply(lambda x: x.get('Fees')).dropna()
        col1, col2 = st.columns(2)
        col1.metric('Total Payment:', f'RM{fees.sum():,.2f}')
        col2.metric('Total Jobs:', fees.__len__())
        clients = df['client'].map(Counter).groupby(df['key']).sum()
        clients = df['client'].apply(lambda x: x.get('cli')).dropna()
        dats = df['date'].map(Counter).groupby(df['key']).sum()
        dats = df['date'].apply(lambda x: x.get('dat')).dropna()
        with st.expander('Dataframe:'):
            st.table(df)

    if selected == 'Job Sheet':
        st.header('Job Sheet Form')
        #st.write("---")
        with st.form('entry_form', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                for client in cli:
                    st.text_input('Client:', placeholder='Please enter client name', key=client)
                for address in add:
                    st.text_input('Address:', placeholder='Please enter client address', key=address)
            with col2:
                for date in dat:
                    st.text_input('Date:', key=date)
                for category in cat:
                    #st.text_input('Category:', key=category)
                    st.selectbox('Category:',('Inspection','Online Survey'), key=category)
            st.write("---")
            for description in des:
                st.text_input('Works Description:', placeholder='Please enter works description here', key=description)

            #with st.expander("Payment:"):
            for payment in pay:
                st.number_input(f"{payment}:", min_value=0, format="%i", key=payment)
            
            submitted = st.form_submit_button('Submit')
            if submitted:
                cli = {client: st.session_state[client] for client in cli}
                add = {address: st.session_state[address] for address in add}
                cat = {category: st.session_state[category] for category in cat}
                des = {description: st.session_state[description] for description in des}
                pay = {payment: st.session_state[payment] for payment in pay}
                dat = {date: st.session_state[date] for date in dat}
                insert_date(dat, cli, add, cat, des, pay)
                st.success('Data Submitted')

# --- HIDE STREAMLIT STYLE ---

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)