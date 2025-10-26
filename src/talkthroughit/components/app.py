import streamlit as st
from streamlit_router import StreamlitRouter
from room import room_page
import uuid

st.set_page_config(page_title="talkthroughsession",layout='wide')

def landing_page():
    st.title("Landing Page")
    if st.button("go to room"):
        session_page = router.build("room_page",{"session_id" : uuid.uuid4()})
        router.redirect(*session_page)
router = StreamlitRouter()
router.register(landing_page, '/')
router.register(room_page, '/room/<string:session_id>')

router.serve()