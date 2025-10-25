import streamlit as st
#from whiteboard import drawableCanvas
from code_editor import code_editor

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
                    st.session_state.tabs.append({"name": new_tab_name, "type": new_tab_type})
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

    add_or_remove_tabs()

    if len(st.session_state.tabs) == 0:
        st.session_state.tabs.append({"name":"default","type" : "canvas"})
    
    try:
        tab_names = [t["name"] for t in st.session_state.tabs]
        for i,tab in enumerate(st.tabs(tab_names)):
            with tab:
                if st.session_state.tabs[i]["type"] == "canvas":
                    pass
                    #drawableCanvas()
                if st.session_state.tabs[i]["type"] == "code":
                    code_editor("\n" * 20)
    except Exception as e:
        st.error(f"An error occurred: {e}")
