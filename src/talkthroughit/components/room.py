
import streamlit as st
from .chatcomponent import chatComponent
from .tabs import tabsComponent
from talkthroughit.rooms.room import get_room

def room_page(router,room_id):
    st.set_page_config(layout="wide")
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)
    col1,col2 = st.columns([5,2],gap='small')
    room_info = get_room(st.session_state.room_id)
    with col1:
        tabsComponent()
    with col2:
        chatComponent(room_info)
