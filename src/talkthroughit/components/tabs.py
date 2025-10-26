import streamlit as st
from code_editor import code_editor
from .whiteboard import whiteboard

def render_tab_content():
    chosen_id = st.session_state.current_tab
    current_tab_index = [i for i, tab in enumerate(st.session_state.tabs) if tab["name"] == chosen_id][0]
    current_tab_data = st.session_state.tabs[current_tab_index]
    st.session_state.current_tab_data = current_tab_data

    with st.container(key='tab-container', border=False):
        if current_tab_data:
            if current_tab_data["type"] == "canvas":
                whiteboard(width=1000,height=700)
            if current_tab_data["type"] == "code":
                response_dict = code_editor(st.session_state.tabs[current_tab_index]["content"])
                if response_dict['text'] != st.session_state.tabs[current_tab_index]["content"]:
                    st.session_state.tabs[current_tab_index]["content"] = response_dict['text']
