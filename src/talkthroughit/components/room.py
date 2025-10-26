
import streamlit as st
from chatcomponent import chatComponent
from tabs import tabsComponent
import random

def room_page(router,session_id):
    col1,col2 = st.columns([4,1],gap='small')
    with col1:
        tabsComponent()
    with col2:
        chatComponent()
