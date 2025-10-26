import streamlit as st
from .chatcomponent import chatComponent
from .tabs import render_tab_content
from talkthroughit.rooms.room import get_room

def room_page(router,room_id):
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    room_info = get_room(st.session_state.room_id)

    st.set_page_config(layout="wide")
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 2rem;
                }
               .main .block-container {
                    background-color: #F0F2F6;
                }
                [data-testid="stSidebar"] {
                    background-color: #FFFFFF;
                }
                /* Sidebar radio button styling */
                div[data-testid="stRadio"] > label > div:first-child {
                    display: none; /* hide the radio circle */
                }
        </style>
        """, unsafe_allow_html=True)

    if "tabs" not in st.session_state:
        st.session_state.tabs = []
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "canvas"

    if len(st.session_state.tabs) == 0:
        st.session_state.tabs.append({"name":"canvas","type" : "canvas", "content": ""})
        st.session_state.tabs.append({"name":"code","type" : "code", "content": ""})

    tab_names = [t["name"] for t in st.session_state.tabs]
    
    with st.sidebar:
        st.title(f"Topic: {room_info.topic}")
        chosen_id = st.radio(
            "Navigation",
            ["canvas","code"],
            label_visibility="collapsed"
        )
        st.session_state.current_tab = chosen_id

    col1,col2 = st.columns([3,1],gap='large')
    with col1:
        render_tab_content()
    with col2:
        chatComponent(room_info)
