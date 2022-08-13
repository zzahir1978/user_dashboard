#from cgitb import text
#from cmath import exp
#from email.utils import collapse_rfc2231_value
#from turtle import update
from __future__ import annotations
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

st.set_page_config('User Dashboard', ':file_folder:', layout='wide')         # https://www.webfx.com/tools/emoji-cheat-sheet/
st.title(':file_folder:' + " " + 'User Dashboard')

# Setting for utility database
uti = ['uti']
dat2 = ['dat2']
exps = ['Cost']
usa = ['Usage']

# Utility Database Interface
DETA_KEY = 'c0jo61nr_Fk3geHfjZYDv53FuxFYaEPjhitTawRVz'              # Key Name: b993nq, Key Description: Project Key: b993nq, Project Key: c0jo61nr_Fk3geHfjZYDv53FuxFYaEPjhitTawRVz
deta = Deta(DETA_KEY)
db2 = deta.Base('utility_db')

def insert_util(uti, dat2, exps, usa, comment):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db2.put({'utility': uti, 'date': dat2, 'expense': exps, 'usage': usa, 'comment': comment})

def fetch_all_utils():
    """Returns a dict of all date"""
    res = db2.fetch()
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

    selected = option_menu(menu_title = None, options = ['Dashboard','Job Sheet','Utility Form','User Info','Body Mass Index'], 
                            icons = ['grid-1x2','calendar2-event','card-checklist','card-checklist','calculator'], orientation='horizontal')

    # Creating Utility Table Dataframe
    df2 = fetch_all_utils()
    df2 = json.dumps(df2)
    df2 = pd.read_json(df2)
    # Creating new columns
    expense_1 = df2['expense'].map(Counter).groupby(df2['key']).sum()
    expense_1 = df2['expense'].apply(lambda x: x.get('Cost')).dropna()
    usage_1 = df2['usage'].map(Counter).groupby(df2['key']).sum()
    usage_1 = df2['usage'].apply(lambda x: x.get('Usage')).dropna()
    utility_1 = df2['utility'].map(Counter).groupby(df2['key']).sum()
    utility_1 = df2['utility'].apply(lambda x: x.get('uti')).dropna()
    date_2 = df2['date'].map(Counter).groupby(df2['key']).sum()
    date_2 = df2['date'].apply(lambda x: x.get('dat2')).dropna()
    # Combined all new columns
    df2_new = pd.merge(date_2, utility_1, left_index=True, right_index=True)
    df2_new = pd.merge(df2_new, expense_1, left_index=True, right_index=True)
    df2_new = pd.merge(df2_new, usage_1, left_index=True, right_index=True)
    df2_new['date'] = pd.to_datetime(df2_new['date'])
    df2_new = df2_new.sort_values(by='date')
    df2_new['date'] = df2_new['date'].astype(str).str.replace('T','-', regex=True)
    # Creating Utility Tables
    df_TNB = df2_new[(df2_new['utility'] == 'TNB')]
    df_AIR = df2_new[(df2_new['utility'] == 'Air Selangor')]
    df_DIGI = df2_new[(df2_new['utility'] == 'DiGi')]
    df_TM = df2_new[(df2_new['utility'] == 'TM')]
    df_IWK = df2_new[(df2_new['utility'] == 'IWK')]
    # ----
    total_tnb = df_TNB['expense'].sum()
    bill_tnb = df_TNB['expense'].__len__()
    total_kwh = df_TNB['usage'].sum()
    total_air = df_AIR['expense'].sum()
    bill_air = df_AIR['expense'].__len__()
    total_m3 = df_AIR['usage'].sum()
    total_digi = df_DIGI['expense'].sum()
    bill_digi = df_DIGI['expense'].__len__()
    total_tm = df_TM['expense'].sum()
    bill_tm = df_TM['expense'].__len__()
    total_iwk = df_IWK['expense'].sum()
    bill_iwk = df_IWK['expense'].__len__()
    
    if selected == 'Dashboard':
        st.header('Summary:')
        st.subheader(':bulb: Utility')                                  # To select other emoji at https://www.webfx.com/tools/emoji-cheat-sheet/

        labels = ['TNB','Air Selangor','Streamyx','DiGi']
        values = [total_tnb, total_air, total_tm, total_digi]

        # Use `hole` to create a donut-like pie chart
        fig_main = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.6,textinfo='label+percent')])
        fig_main.update_layout(title_text='',title_x=0.5,font=dict(family="Helvetica", size=10),showlegend=False,
                                annotations=[dict(text='Utilities Cost', x=0.5, y=0.5, font_size=20, showarrow=False)])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('TNB', f'RM{total_tnb:,.2f}')
            st.metric('Air Selangor', f'RM{total_air:,.2f}')
            
        with col2:
            st.metric('DiGi', f'RM{total_digi:,.2f}')
            st.metric('TM Streamyx', f'RM{total_tm:,.2f}')
            
        with col3:
            st.metric('IWK', f'RM{total_iwk:,.2f}')
            st.metric('Total Utility Cost', f'RM{(total_tnb+total_air+total_tm+total_digi+total_iwk):,.2f}')

        st.plotly_chart(fig_main, use_container_width = True)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.write('TNB')
        col1.metric('No. Of Bills', f'{bill_tnb}')
        col1.metric('Average Cost', f'{(total_tnb/bill_tnb):,.2f}')
        col1.metric('kWh', f'{total_kwh:,.0f}')
        # ----
        col2.write('Air Selangor')
        col2.metric('No. Of Bills', f'{bill_air}')
        col2.metric('Average Cost', f'{(total_air/bill_air):,.2f}')
        col2.metric('m3', f'{total_m3:,.0f}')
        # ----
        col3.write('Digi')
        col3.metric('No. Of Bills', f'{bill_digi}')
        col3.metric('Average Cost', f'{(total_digi/bill_digi):,.2f}')
        col3.metric('TNB Rate (RM/kWh)', f'{(total_tnb/total_kwh):,.2f}')
        # ----
        col4.write('TM')
        col4.metric('No. Of Bills', f'{bill_tm}')
        col4.metric('Average Cost', f'{(total_tm/bill_tm):,.2f}')
        col4.metric('Air Selangor Rate (RM/m3)', f'{(total_air/total_m3):,.2f}')
        # ----
        col5.write('IWK')
        
        col5.metric('No. Of Bills', f'{bill_iwk}')
        col5.metric('Average Cost', f'{(total_iwk/bill_iwk):,.2f}')
        
        with st.expander('TNB Dataframe:'):
            # Graph
            fig_tnb = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_tnb.add_trace(go.Bar(x = df_TNB['date'], y = df_TNB['expense'],name='RM'))
            fig_tnb.add_trace(go.Scatter(x = df_TNB['date'], y = df_TNB['usage'],name='kWh',
                fill='tozeroy',mode='lines',line = dict(color='red', width=1)), secondary_y=True)
            fig_tnb.add_trace(go.Scatter(x = df_TNB['date'], y = df_TNB['usage'],name='kWh',
                mode='lines',line = dict(color='black', width=2)), secondary_y=True)
            fig_tnb.update_layout(height=350,title_text='Annual Electricity Consumption (RM VS kWh)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
                yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
            fig_tnb.update_annotations(font=dict(family="Helvetica", size=10))
            fig_tnb.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_tnb.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            st.plotly_chart(fig_tnb, use_container_width=True)
            # Table
            fig_table_tnb = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_TNB.columns),fill_color='paleturquoise',align='center'),
                                cells=dict(values=[df_TNB.date, df_TNB.utility, df_TNB.expense, df_TNB.usage],fill_color='lavender',align='center'))])
            fig_table_tnb.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_tnb, use_container_width=True)
        
        with st.expander('Air Selangor Dataframe'):
            # Graph
            fig_air = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_air.add_trace(go.Bar(x = df_AIR['date'], y = df_AIR['expense'],name='RM'))
            fig_air.add_trace(go.Scatter(x = df_AIR['date'], y = df_AIR['usage'],name='m3',
                fill='tozeroy',mode='lines',line = dict(color='red', width=1)), secondary_y=True)
            fig_air.add_trace(go.Scatter(x = df_AIR['date'], y = df_AIR['usage'],name='m3',
                mode='lines',line = dict(color='black', width=2)), secondary_y=True)
            fig_air.update_layout(height=350,title_text='Annual Water Consumption (RM VS m3)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
                yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
            fig_air.update_annotations(font=dict(family="Helvetica", size=10))
            fig_air.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_air.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            st.plotly_chart(fig_air, use_container_width=True)
            # Table
            fig_table_air = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_AIR.columns),fill_color='paleturquoise',align='center'),
                                cells=dict(values=[df_AIR.date, df_AIR.utility, df_AIR.expense, df_AIR.usage],fill_color='lavender',align='center'))])
            fig_table_air.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_air, use_container_width=True)

        with st.expander('DiGi Dataframe'):
            # Graph
            fig_digi = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_digi.add_trace(go.Bar(x = df_DIGI['date'], y = df_DIGI['expense'],name='RM'))
            fig_digi.update_layout(height=350,title_text='Annual DiGi Consumption (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
                yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
            fig_digi.update_annotations(font=dict(family="Helvetica", size=10))
            fig_digi.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_digi.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            st.plotly_chart(fig_digi, use_container_width=True)
            # Table
            fig_table_digi = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_DIGI.columns),fill_color='paleturquoise',align='center'),
                                cells=dict(values=[df_DIGI.date, df_DIGI.utility, df_DIGI.expense, df_DIGI.usage],fill_color='lavender',align='center'))])
            fig_table_digi.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_digi, use_container_width=True)

        with st.expander('TM Dataframe'):
            # Graph
            fig_tm = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_tm.add_trace(go.Bar(x = df_TM['date'], y = df_TM['expense'],name='RM'))
            fig_tm.update_layout(height=350,title_text='Annual TM Consumption (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
                yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
            fig_tm.update_annotations(font=dict(family="Helvetica", size=10))
            fig_tm.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_tm.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            st.plotly_chart(fig_tm, use_container_width=True)
            # Table
            fig_table_tm = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_TM.columns),fill_color='paleturquoise',align='center'),
                                cells=dict(values=[df_TM.date, df_TM.utility, df_TM.expense, df_TM.usage],fill_color='lavender',align='center'))])
            fig_table_tm.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_tm, use_container_width=True)
        
        with st.expander('IWK Dataframe'):
            # Graph
            fig_iwk = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_iwk.add_trace(go.Bar(x = df_IWK['date'], y = df_IWK['expense'],name='RM'))
            fig_iwk.update_layout(height=350,title_text='Annual IWK Consumption (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
                yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
            fig_iwk.update_annotations(font=dict(family="Helvetica", size=10))
            fig_iwk.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_iwk.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            st.plotly_chart(fig_iwk, use_container_width=True)
            # Table
            fig_table_iwk = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_IWK.columns),fill_color='paleturquoise',align='center'),
                                cells=dict(values=[df_IWK.date, df_IWK.utility, df_IWK.expense, df_IWK.usage],fill_color='lavender',align='center'))])
            fig_table_iwk.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_iwk, use_container_width=True)

    if selected == 'Job Sheet':

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

        def insert_job(dat, cli, add, cat, des, pay, remark):
            """Returns the user on a successful user creation, otherwise raises and error"""
            return db.put({'date': dat, 'client': cli, 'address': add, 'category': cat, 'description': des,'payment': pay, 'remark': remark})

        def fetch_all_jobs():
            """Returns a dict of all date"""
            res = db.fetch()
            return res.items

        # Creating Job Sheet Table Dataframe
        df = fetch_all_jobs()
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
        # -----
        clients = pd.merge(client_1, payment_1, left_index=True, right_index=True)
        clients = clients.groupby('client').sum()
        clients['payment'] = clients['payment'].map('RM{:,.2f}'.format)
        # ----
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
        # ----
        fees_total = df['payment'].map(Counter).groupby(df['key']).sum()
        fees_total = df['payment'].apply(lambda x: x.get('Fees')).dropna()
        fees_2020 = df_2020['payment'].map(Counter).groupby(df_2020['key']).sum()
        fees_2020 = df_2020['payment'].apply(lambda x: x.get('Fees')).dropna()
        fees_2021 = df_2021['payment'].map(Counter).groupby(df_2021['key']).sum()
        fees_2021 = df_2021['payment'].apply(lambda x: x.get('Fees')).dropna()
        fees_2022 = df_2022['payment'].map(Counter).groupby(df_2022['key']).sum()
        fees_2022 = df_2022['payment'].apply(lambda x: x.get('Fees')).dropna()

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
            
            remark = st.text_area('Remarks:', placeholder='Enter a comment here...')
            
            submitted_job = st.form_submit_button('Submit')
            if submitted_job:
                cli = {client: st.session_state[client] for client in cli}
                add = {address: st.session_state[address] for address in add}
                cat = {category: st.session_state[category] for category in cat}
                des = {description: st.session_state[description] for description in des}
                pay = {payment: st.session_state[payment] for payment in pay}
                dat = {date: st.session_state[date] for date in dat}
                insert_job(dat, cli, add, cat, des, pay, remark)
                st.success('Data saved!')
            
        st.subheader(':books: Job Sheet')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric('Total Payment', f'RM{fees_total.sum():,.2f}')
        col2.metric('Total Jobs', fees_total.__len__())
        col3.metric('Average Payment', f'RM{(fees_total.sum()/fees_total.__len__()):,.2f}')

        with st.expander('Job Sheet Summary:'):
            col1, col2, col3 = st.columns(3)
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
        with st.expander('Job Sheet Dataframe:'):
            fig_table_dataframe = go.Figure(
                data=[go.Table(columnwidth=[1,1,1,1,2,1],header=dict(values=list(df_new.columns),fill_color='paleturquoise',align='center'),
                cells=dict(values=[df_new.address, df_new.category, df_new.client, df_new.date, df_new.description, df_new.payment],
                fill_color='lavender',align='left'))])
            fig_table_dataframe.update_layout(margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_table_dataframe, use_container_width=True)

    if selected == 'Utility Form':
        st.header('Utility Expenses Form')
        with st.form('entry_form', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                for utility in uti:
                    st.selectbox('Utility Provider:',('TNB','Air Selangor','TM','DiGi','IWK') , key=utility)
                for date2 in dat2:
                    st.text_input('Date:', placeholder='Date format in mm/dd/yy',key=date2)
            with col2:
                for expense in exps:
                    st.number_input(f"{expense}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=expense)
                for usage in usa:
                    st.number_input(f"{usage}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.0f", key=usage)
            
            comment = st.text_area('Remarks:', placeholder='Enter a comment here...')

            submitted_util = st.form_submit_button('Submit')
            if submitted_util:
                uti = {utility: st.session_state[utility] for utility in uti}
                dat2 = {date2: st.session_state[date2] for date2 in dat2}
                exps = {expense: st.session_state[expense] for expense in exps}
                usa = {usage: st.session_state[usage] for usage in usa}
                insert_util(uti,dat2,exps,usa,comment)
                st.success('Data saved!')

    if selected == 'User Info':
        # Database connection
        DETA_KEY = "c0jo61nr_BhSm5qHprUP75vRSdEmumYfoS1KMCtQW"
        # Initialize with a project key
        deta = Deta(DETA_KEY)
        # This is how to create/connect a database
        db = deta.Base("test_db")
        # Database function
        # Insert new data to db
        def insert_data(username, name, email,address,ic,dob):
            """Returns the user on a successful user creation, otherwise raises and error"""
            return db.put({"key": username, "name": name, "email": email, "address": address, "ic": ic, "dob": dob})
        # Call all data from db
        def fetch_all_data():
            """Returns a dict of all periods"""
            res = db.fetch()
            return res.items
        # Update data from db
        def update_data(username, updates):
            """If the item is updated, returns None. Otherwise, an exception is raised"""
            return db.update(updates, username)
        # Delete data from db
        def delete_data(username):
            """Always returns None, even if the key does not exist"""
            return db.delete(username)

        with st.form('entry_form', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input('Name:', placeholder='Please enter full name')
                ic = st.text_input('Identiy Card No.:', placeholder='Please enter identity card no.')
                address = st.text_area('Address:', placeholder='Please enter address')    
                
            with col2:
                dob = st.text_input('Date Of Birth:', placeholder='Please enter date of birth in mm/dd/yy')
                email = st.text_input('Email:', placeholder='Please enter email address')
                username = st.text_input('Username:', placeholder='Please enter username')
                
            col1, col2, col3 = st.columns(3)
            with col1:    
                saved_data = st.form_submit_button('Submit:')
                if saved_data:
                    insert_data(username, name, email,address,ic,dob)
                    st.success('Data saved!')
            with col2:
                updates_data = st.form_submit_button('Update:')
                if updates_data:
                    username_1 = username
                    name_1 = 'name'
                    nam = name
                    email_1 = 'email'
                    ema = email
                    address_1 = 'address'
                    add = address
                    ic_1 = 'ic'
                    ics = ic
                    dob_1 = 'dob'
                    dob = dob
                    update_data(username, updates={name_1:nam, email_1:ema, address_1:add, ic_1:ics, dob_1:dob})
                    st.success('Data updates!')
            
            with col3:
                del_data = st.form_submit_button('Delete:')
                st.write('Key in username to delete!')
                if del_data:
                    username_2 = username
                    delete_data(username)
                    st.success('Data delete!')

        st.subheader('Table Dataframe:')
        data = fetch_all_data()
        #data = json.dumps(data)
        #data = pd.read_json(data)
        #data = data[['key','name','email','ic','dob','address']]
        #data.rename(columns = {'key':'username'}, inplace=True)
        #data = data.sort_values(by='name').reset_index(drop=True)
        st.table(data)

    if selected == 'Body Mass Index':
        outside_expander_area = st.container()
        state = st.session_state
        if 'WEIGHT' not in state:
            state.WEIGHT = 52.0
        if 'HEIGHT' not in state:
            state.HEIGHT = 1.65

        def _set_values_cb():
            state.WEIGHT = state['weight']
            state.HEIGHT = state['height']

        with outside_expander_area:
            c1, c2 = st.columns([1,1])
            with c1:
                guage = st.empty()
            with c2:
                state.WEIGHT = st.number_input('Enter weight (kg)', min_value=50.0, max_value=150.0, value=state.WEIGHT, step=0.5, on_change=_set_values_cb, key='weight')
                state.HEIGHT = st.number_input('Enter height (m)', min_value=1.0, max_value=2.5, value=state.HEIGHT, step=0.1, on_change=_set_values_cb, key='height')

        BMI = round(state.WEIGHT/(state.HEIGHT**2), 1)

        bmi_thresholds = [13, 18.5, 25, 30, 43]
        level_labels = ['Severe Underweight', 'Underweight','Normal','Overweight','Obesity', 'Severe Obesity']

        if BMI <= bmi_thresholds[0]:
            level = level_labels[0]
        elif BMI <= bmi_thresholds[1]:
            level = level_labels[1]
        elif BMI <= bmi_thresholds[2]:
            level = level_labels[2]
        elif BMI <= bmi_thresholds[3]:
            level = level_labels[3]
        elif BMI <= bmi_thresholds[4]:
            level = level_labels[4]
        else:
            level = level_labels[5]

        bmi_gauge_lower = 13 # 0 degrees
        bmi_gauge_upper = 43 # 180 degrees

        bmi_guage_range = (bmi_gauge_upper - bmi_gauge_lower)
        BMI_adjusted = BMI if (BMI >= bmi_gauge_lower and BMI <= bmi_gauge_upper) else (
            bmi_gauge_lower if BMI < bmi_gauge_lower else bmi_gauge_upper
        )
        dial_rotation = round(((BMI_adjusted - bmi_gauge_lower) / bmi_guage_range) * 180.0, 1)

        html = f"""
        <html><body>
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="300px" height="163px" viewBox="0 0 300 163">
        <g transform="translate(18,18)" style="font-family:arial,helvetica,sans-serif;font-size: 12px;">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7"></polygon>
                </marker>
                <path id="curvetxt1" d="M-4 140 A140 140, 0, 0, 1, 284 140" style="fill: none;"></path>
                <path id="curvetxt2" d="M33 43.6 A140 140, 0, 0, 1, 280 140" style="fill: #none;"></path>
                <path id="curvetxt3" d="M95 3 A140 140, 0, 0, 1, 284 140" style="fill: #none;"></path>
                <path id="curvetxt4" d="M235.4 33 A140 140, 0, 0, 1, 284 140" style="fill: #none;"></path>
            </defs>
            <path d="M0 140 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#bc2020"></path>
            <path d="M6.9 96.7 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#d38888"></path>
            <path d="M12.1 83.1 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#ffe400"></path>
            <path d="M22.6 63.8 A140 140, 0, 0, 1, 96.7 6.9 L140 140 Z" fill="#008137"></path>
            <path d="M96.7 6.9 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#ffe400"></path>
            <path d="M169.1 3.1 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#d38888"></path>
            <path d="M233.7 36 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#bc2020"></path>
            <path d="M273.1 96.7 A140 140, 0, 0, 1, 280 140 L140 140 Z" fill="#8a0101"></path>
            <path d="M45 140 A90 90, 0, 0, 1, 230 140 Z" fill="#fff"></path>
            <circle cx="140" cy="140" r="5" fill="#666"></circle>

            <g style="paint-order: stroke;stroke: #fff;stroke-width: 2px;">
                <text x="25" y="111" transform="rotate(-72, 25, 111)">16</text>
                <text x="30" y="96" transform="rotate(-66, 30, 96)">17</text>
                <text x="35" y="83" transform="rotate(-57, 35, 83)">18.5</text>
                <text x="97" y="29" transform="rotate(-18, 97, 29)">25</text>
                <text x="157" y="20" transform="rotate(12, 157, 20)">30</text>
                <text x="214" y="45" transform="rotate(42, 214, 45)">35</text>
                <text x="252" y="95" transform="rotate(72, 252, 95)">40</text>
            </g>

            <g style="font-size: 14px;">
                <text><textPath xlink:href="#curvetxt1">Underweight</textPath></text>
                <text><textPath xlink:href="#curvetxt2">Normal</textPath></text>
                <text><textPath xlink:href="#curvetxt3">Overweight</textPath></text>
                <text><textPath xlink:href="#curvetxt4">Obesity</textPath></text>
            </g>

            <line x1="140" y1="140" x2="65" y2="140" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)">
                <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="0 140 140" to="{dial_rotation} 140 140" dur="1s" fill="freeze" repeatCount="1"></animateTransform>
            </line>

            <text x="67" y="120" style="font-size: 30px;font-weight:bold;color:#000;">BMI = {BMI}</text>
        </g>
        </svg>
        </body></html>
        """

        with outside_expander_area:
            import streamlit.components.v1 as components

            with guage:
                components.html(html.replace('\n',''))

            st.subheader(f'BMI level is {level} ({BMI})')
            # st.caption(f'Rotation: {dial_rotation} degrees')

# --- HIDE STREAMLIT STYLE ---

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)