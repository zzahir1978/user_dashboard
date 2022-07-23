from cgitb import text
from email.utils import collapse_rfc2231_value
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
import calendar
from datetime import datetime

st.set_page_config('Job Sheet Dashboard', ':file_folder:', layout='wide')         # https://www.webfx.com/tools/emoji-cheat-sheet/
st.title(':file_folder:' + " " + 'Job Sheet Dashboard')

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
        # Creating new columns
        address_1 = df['address'].map(Counter).groupby(df['key']).sum()
        address_1 = df['address'].apply(lambda x: x.get('add')).dropna()
        category_1 = df['category'].map(Counter).groupby(df['key']).sum()
        category_1 = df['category'].apply(lambda x: x.get('cat')).dropna()
        client_1 = df['client'].map(Counter).groupby(df['key']).sum()
        client_1 = df['client'].apply(lambda x: x.get('cli')).dropna()
        date_1 = df['date'].map(Counter).groupby(df['key']).sum()
        date_1 = df['date'].apply(lambda x: x.get('dat')).dropna()
        description_1 = df['description'].map(Counter).groupby(df['key']).sum()
        description_1 = df['description'].apply(lambda x: x.get('des')).dropna()
        payment_1 = df['payment'].map(Counter).groupby(df['key']).sum()
        payment_1 = df['payment'].apply(lambda x: x.get('Fees')).dropna()
        # Combined all new columns
        df_new = pd.merge(address_1, category_1, left_index=True, right_index=True)
        df_new = pd.merge(df_new, client_1, left_index=True, right_index=True)
        df_new = pd.merge(df_new, date_1, left_index=True, right_index=True)
        df_new = pd.merge(df_new, description_1, left_index=True, right_index=True)
        df_new = pd.merge(df_new, payment_1, left_index=True, right_index=True)
        df_new['payment'] = df_new['payment'].map('RM{:,.2f}'.format)
        df_new['date'] = pd.to_datetime(df_new['date'])
        df_new = df_new.sort_values(by='date')
        df_new['date'] = df_new['date'].astype(str).str.replace('T','-', regex=True)

        clients = pd.merge(client_1, payment_1, left_index=True, right_index=True)
        clients = clients.groupby('client').sum()
        clients['payment'] = clients['payment'].map('RM{:,.2f}'.format)

        df = pd.merge(df, date_1, left_index=True, right_index=True)
        df['date_y'] = pd.to_datetime(df['date_y'])
        # Creating yearly table
        # 2020
        df_2020 = df[(df['date_y'] >= "2020-01-01") & (df['date_y'] <="2020-12-01")]
        df_2020 = df_2020.sort_values(by='date_y')
        # 2021
        df_2021 = df[(df['date_y'] >= "2021-01-01") & (df['date_y'] <="2021-12-01")]
        df_2021 = df_2021.sort_values(by='date_y')
        # 2022
        df_2022 = df[(df['date_y'] >= "2022-01-01") & (df['date_y'] <="2022-12-01")]
        df_2022 = df_2022.sort_values(by='date_y')
        
        fees_total = df['payment'].map(Counter).groupby(df['key']).sum()
        fees_total = df['payment'].apply(lambda x: x.get('Fees')).dropna()
        fees_2020 = df_2020['payment'].map(Counter).groupby(df_2020['key']).sum()
        fees_2020 = df_2020['payment'].apply(lambda x: x.get('Fees')).dropna()
        fees_2021 = df_2021['payment'].map(Counter).groupby(df_2021['key']).sum()
        fees_2021 = df_2021['payment'].apply(lambda x: x.get('Fees')).dropna()
        fees_2022 = df_2022['payment'].map(Counter).groupby(df_2022['key']).sum()
        fees_2022 = df_2022['payment'].apply(lambda x: x.get('Fees')).dropna()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader('Year 2020')
            col1.metric('Payment:', f'RM{fees_2020.sum():,.2f}')
            col1.metric('Jobs:', fees_2020.__len__())
        with col2:
            st.subheader('Year 2021')
            col2.metric('Payment:', f'RM{fees_2021.sum():,.2f}')
            col2.metric('Jobs:', fees_2021.__len__())
        with col3:
            st.subheader('Year 2022')
            col3.metric('Payment:', f'RM{fees_2022.sum():,.2f}')
            col3.metric('Jobs:', fees_2022.__len__())
        with col4:
            st.subheader('Total')
            col4.metric('Payment:', f'RM{fees_total.sum():,.2f}')
            col4.metric('Jobs:', fees_total.__len__())
        
        # Graph
        fig_bar = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
        fig_bar.add_trace(go.Bar(x = ['2020','2021','2022'], y = [fees_2020.sum(),fees_2021.sum(),fees_2022.sum()],name='RM', 
            text=[fees_2020.sum(),fees_2021.sum(),fees_2022.sum()]))
        fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='auto')
        fig_bar.update_layout(title_text='Annual Fees (RM)',title_x=0.5, height=350, font=dict(family="Helvetica", size=10),
                            xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
        fig_bar.update_annotations(font=dict(family="Helvetica", size=10))
        fig_bar.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
        fig_bar.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
        # PIE CHART Cost
        fig_pie = make_subplots(specs=[[{"type": "domain"}]])
        fig_pie.add_trace(go.Pie(values=[fees_2020.sum(),fees_2021.sum(),fees_2022.sum()],labels=['2020','2021','2022'],textposition='inside',
                        textinfo='label+percent'),row=1, col=1)
        fig_pie.update_annotations(font=dict(family="Helvetica", size=10))
        fig_pie.update_layout(height=350,showlegend=False,title_text='Annual Fees (%)',title_x=0.5,font=dict(family="Helvetica", size=10))            
        # Chart Presentation
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig_bar, use_container_width=True)
        col2.plotly_chart(fig_pie, use_container_width=True)

        with st.expander('List Of Clients:'):
            clients = clients.reset_index()    
            fig_table_client = go.Figure(data=[go.Table(columnwidth=[1,1], header=dict(values=list(clients.columns),fill_color='paleturquoise',align='center'),
                                cells=dict(values=[clients.client, clients.payment],fill_color='lavender',align='left'))])
            fig_table_client.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_client, use_container_width=True)
            #st.dataframe(clients.reset_index())
        with st.expander('Dataframe:'):
            fig_table_dataframe = go.Figure(
                data=[go.Table(columnwidth=[1,1,1,1,2,1],header=dict(values=list(df_new.columns),fill_color='paleturquoise',align='center'),
                cells=dict(values=[df_new.address, df_new.category, df_new.client, df_new.date, df_new.description, df_new.payment],
                fill_color='lavender',align='left'))])
            fig_table_dataframe.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_dataframe, use_container_width=True)
            #st.dataframe(df_new)

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
                    st.text_input('Date:', placeholder='Date format in mm/dd/yy',key=date)
                for category in cat:
                    #st.text_input('Category:', key=category)
                    st.selectbox('Category:',('Inspection','Online Survey','Voice Recording','Website Design'), key=category)
            st.write("---")
            for description in des:
                st.text_area('Works Description:', placeholder='Please enter works description here', key=description)

            #with st.expander("Payment:"):
            for payment in pay:
                st.number_input(f"{payment}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=payment)
            
            submitted = st.form_submit_button('Submit')
            if submitted:
                cli = {client: st.session_state[client] for client in cli}
                add = {address: st.session_state[address] for address in add}
                cat = {category: st.session_state[category] for category in cat}
                des = {description: st.session_state[description] for description in des}
                pay = {payment: st.session_state[payment] for payment in pay}
                dat = {date: st.session_state[date] for date in dat}
                insert_date(dat, cli, add, cat, des, pay)
                st.success('Data saved!')

# --- HIDE STREAMLIT STYLE ---

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)