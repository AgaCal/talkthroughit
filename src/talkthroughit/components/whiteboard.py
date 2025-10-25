import streamlit as st
from math import ceil
from streamlit_drawable_canvas import st_canvas

stroke_width = "3"
stroke_color = "#000000"
drawing_mode = "freedraw"

canvas_result = st_canvas(
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    fill_color=stroke_color,
    background_color="#ffffff",
    update_streamlit=True,
    width=1000,
    height=750,
    drawing_mode=drawing_mode,
    key="canvas",
)

drawing_mode = st.radio(
    label="Drawing tool:", 
    options=("freedraw", "line", "rect", "circle", "transform"),
    horizontal = True
)

stroke_width = st.slider("Stroke width: ", 1, 25, 3)

tmp_stroke_color = st.color_picker("Stroke color hex: ")
stroke_opacity = st.slider("Stroke opacity: ", min_value=0.0, max_value=1.0, value=1.0)

stroke_color = tmp_stroke_color + (hex(ceil(stroke_opacity * 255))[2:]).zfill(2)

print(stroke_color)

if canvas_result.image_data is not None:
    st.image(canvas_result.image_data)
