import streamlit as st
from math import ceil
from streamlit_drawable_canvas import st_canvas
from streamlit_option_menu import option_menu
from talkthroughit.components.color_selector import color_select
from PIL import Image
from io import BytesIO
import base64

TRANSPARENT = "#00000000"
WHITE = "#ffffff"

def whiteboard(width = 500, height = 500):
    '''
    a whiteboard component using streamlit-drawable-canvas
    doesn't return anything, but saves the current image as a base64 string in st.session_state.current_tab_data["content"]
    width and height are the dimensions of the canvas - not the entire component! menu extends beyond that
    make sure that the entire canvas fits in the screen!!! otherwise there's some weird behavior that's not worth fixing right now
    '''
    
    whiteboard_container = st.container()

    with whiteboard_container:
        col1, col2 = st.columns([5,3], vertical_alignment='top')

    with col1:

        def select_drawing_mode():
            drawing_modes = {
                "freedraw": "pencil",
                "line": "slash-lg",
                "rect": "square",
                "circle": "circle",
                "transform": "hand-index-thumb"
                }

            return option_menu(
                menu_title=None,
                options=list(drawing_modes.keys()),
                icons=list(drawing_modes.values()),
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles= {
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"font-size": "20px", "justify-content": "center"},
                    "nav-link": { "font-size": "0px", "justify-content": "center", "margin":"0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#77dfd3"},
                }
            )

        drawing_mode = select_drawing_mode()

    with col2:
        width_col, opacity_col = st.columns(2)

        with width_col:
            stroke_width = st.slider(label="Width", min_value=1, max_value=25, value=3)

        with opacity_col:
            stroke_opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=1.0)
        
        if drawing_mode in ["rect", "circle"]:
            fill = st.checkbox(label = "Fill?", value=True)
        else:
            fill = False
            st.markdown('<div style="height: 40px;">&nbsp;</div>', unsafe_allow_html=True)

    with col1:
        def select_stoke_color():
            tmp_stroke_color = color_select()
            return tmp_stroke_color, tmp_stroke_color + (hex(ceil(stroke_opacity * 255))[2:]).zfill(2)

        tmp_stroke_color, stroke_color = select_stoke_color()

    with whiteboard_container:
        canvas_result = st_canvas(
            stroke_width=stroke_width,
            stroke_color=stroke_color if not fill else TRANSPARENT,
            fill_color= stroke_color if fill else TRANSPARENT,
            background_color=WHITE,
            update_streamlit=True,
            width=width,
            height=height,
            drawing_mode=drawing_mode,
            key="canvas",
        )

    if canvas_result.image_data is not None:
        img = Image.fromarray((canvas_result.image_data).astype('uint8'), 'RGBA')

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        st.session_state.current_tab_data["content"] = img_str

if __name__ == "__main__":
    st.session_state.current_tab_data = dict()
    whiteboard(width=750)
