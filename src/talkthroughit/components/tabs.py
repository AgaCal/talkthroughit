import streamlit as st
import extra_streamlit_components as stx
from code_editor import code_editor
from .whiteboard import whiteboard

def add_or_remove_tabs():
    with st.expander("Add or remove a tab"):
        # Create tab row
        st.write("Create a new tab")
        create_col1, create_col2, create_col3 = st.columns([2, 2, 1])
        with create_col1:
            new_tab_name = st.text_input("Enter new tab name", key="new_tab_name")
        with create_col2:
            new_tab_type = st.selectbox("Select tab type", ["canvas", "code"], key="new_tab_type")
        with create_col3:
            st.container(height=10,border=False)
            if st.button("Create"):
                if new_tab_name:
                    st.session_state.tabs.append({"name": new_tab_name, "type": new_tab_type, "content": ""})
                    st.rerun()

        # Delete tab row
        st.write("Delete a tab")
        delete_col1, delete_col2 = st.columns([4, 1])
        with delete_col1:
            tabs_to_delete = [tab["name"] for tab in st.session_state.tabs if tab["name"] != "default"]
            if tabs_to_delete:
                tab_to_delete = st.selectbox("Select tab to delete", tabs_to_delete)
        with delete_col2:
            if tabs_to_delete:
                st.container(height=10,border=False)
                if st.button("Delete"):
                    st.session_state.tabs = [tab for tab in st.session_state.tabs if tab["name"] != tab_to_delete]
                    st.rerun()
            else:
                st.write("No tabs to delete")

def tabsComponent():
    if "tabs" not in st.session_state:
        st.session_state.tabs = []
    
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "default"

    add_or_remove_tabs()

    if len(st.session_state.tabs) == 0:
        st.session_state.tabs.append({"name":"default","type" : "canvas", "content": ""})
    
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
            print(message)
            if current_tab_data["type"] == "canvas":
                whiteboard()
            if current_tab_data["type"] == "code":
                response_dict = code_editor(st.session_state.tabs[current_tab_index]["content"])
                if response_dict['text'] != st.session_state.tabs[current_tab_index]["content"]:
                    st.session_state.tabs[current_tab_index]["content"] = response_dict['text']

    except Exception as e:
        st.error(f"An error occurred: {e}")