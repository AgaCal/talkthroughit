import streamlit as st
from code_editor import code_editor
from .whiteboard import whiteboard

def render_tab_content():
    chosen_id = st.session_state.current_tab
    current_tab_data = next((tab for tab in st.session_state.tabs if tab["name"] == chosen_id), None)
    current_tab_index = next((i for i, tab in enumerate(st.session_state.tabs) if tab["name"] == chosen_id), None)

    st.session_state.current_tab_data = current_tab_data
    if current_tab_data:
        if current_tab_data["type"] == "canvas":
            whiteboard(width=1000,height=400)
        if current_tab_data["type"] == "code":
            response_dict = code_editor(st.session_state.tabs[current_tab_index]["content"])
            if response_dict['text'] != st.session_state.tabs[current_tab_index]["content"]:
                st.session_state.tabs[current_tab_index]["content"] = response_dict['text']