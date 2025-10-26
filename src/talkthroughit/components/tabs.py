import streamlit as st
import extra_streamlit_components as stx
from code_editor import code_editor
from .whiteboard import whiteboard


def tabsComponent():
    if "tabs" not in st.session_state:
        st.session_state.tabs = []
    
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "canvas"

    if len(st.session_state.tabs) == 0:
        st.session_state.tabs.append({"name":"canvas","type" : "canvas", "content": ""})
        st.session_state.tabs.append({"name":"code","type" : "code", "content": ""})
    try:
        tab_data = [stx.TabBarItemData(id=t["name"], title=t["name"], description="") for t in st.session_state.tabs]
        chosen_id = stx.tab_bar(data=tab_data, default=st.session_state.current_tab)
        st.session_state.current_tab = chosen_id

        current_tab_data = next((tab for tab in st.session_state.tabs if tab["name"] == chosen_id), None)
        current_tab_index = next((i for i, tab in enumerate(st.session_state.tabs) if tab["name"] == chosen_id), None)

        st.session_state.current_tab_data = current_tab_data
        if current_tab_data:
            message = ""
            if "text_from_audio" in st.session_state:
                for audio_message,sent in st.session_state.text_from_audio:
                    if not sent:
                        message += audio_message + "\n"
                        sent = True
            if current_tab_data["type"] == "canvas":
                whiteboard(width=800,height=500)
            if current_tab_data["type"] == "code":
                response_dict = code_editor(st.session_state.tabs[current_tab_index]["content"])
                if response_dict['text'] != st.session_state.tabs[current_tab_index]["content"]:
                    st.session_state.tabs[current_tab_index]["content"] = response_dict['text']

    except Exception as e:
        st.error(f"An error occurred: {e}")