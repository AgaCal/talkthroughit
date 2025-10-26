import streamlit as st
from math import ceil
from streamlit_drawable_canvas import st_canvas
from streamlit_option_menu import option_menu
from .color_selector import color_select # type: ignore -- it's importing fine, but vs code is being weird about it

TRANSPARENT = "#00000000"
WHITE = "#ffffff"

def whiteboard(width = 500, height = 500) -> st_canvas:
    '''
    a whiteboard component using streamlit-drawable-canvas
    returns the canvas object, to get the image data, use canvas_result.image_data
    buggy and resets on some interactions, will probably be fixed once i save stuff in session state somehow 

    width and height are the dimensions of the canvas - not the entire component! menu extends beyond that

    make sure that the entire canvas fits in the screen!!! otherwise there's some weird behavior that's not worth fixing right now
    '''
    # to display canvas
    canvas_placeholder = st.empty()
    col1, col2 = st.columns(2)

    with col2:
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
                    "icon": {"font-size": "20px", "justify-content": "center"},
                    "nav-link": { "font-size": "0px", "justify-content": "center"}
                }
            )
        
        drawing_mode = select_drawing_mode()

    with col1:

        label_col, slider_col = st.columns([1,3], vertical_alignment="center")

        with label_col:
            st.markdown("Width:")
            st.markdown("Opacity:")

        with slider_col:
            stroke_width = st.slider(label="Width", label_visibility="collapsed", min_value=1, max_value=25, value=3)
            stroke_opacity = st.slider("Opacity", label_visibility="collapsed", min_value=0.0, max_value=1.0, value=1.0)
        fill = st.checkbox(label = "Fill?", value=True) if drawing_mode in ["rect", "circle"] else False 

    with col2:
        _, tmp_col_2, _ = st.columns([1,10,1])

        def select_stoke_color():
            tmp_stroke_color = color_select()
            return tmp_stroke_color + (hex(ceil(stroke_opacity * 255))[2:]).zfill(2)
        
        with (tmp_col_2):
            stroke_color = select_stoke_color()

    with canvas_placeholder.container():
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
    whiteboard(width=750)