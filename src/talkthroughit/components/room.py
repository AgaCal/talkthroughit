import streamlit as st
from .chatcomponent import chatComponent
from .tabs import render_tab_content
from talkthroughit.rooms.room import get_room
from streamlit_option_menu import option_menu

def room_page(router,room_id):
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    room_info = get_room(room_id)

    st.set_page_config(layout="wide")

    # For some reason using .html() doesn't work at all lol
    with open('src/talkthroughit/static/styles.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
        chosen_id = option_menu(
            menu_title=None,
            options=["canvas","code"],
            icons=["marker-tip","code"],
        )
        st.session_state.current_tab = chosen_id

    with st.container(key='main-container'):
        col1,col2 = st.columns([0.7,0.3],gap='large')
        with col1:
            render_tab_content()
        with col2:
            chatComponent(room_info,room_id)
