import streamlit as st

# list of colors to choose from
colors = [
    "#ffffff",
    "#bdbdbd",
    "#000000",
    "#77dfd3",
    "#e977ad",
    "#7a4bef",
    "#d9534f",
    "#f0ad4e",
    "#eeda6e",
    "#8bc34a",
    "#5bc0de",
    "#428bca",
]

def color_select():
    # st radio to select color - but we will hijack the default dots with CSS
    stroke_color = st.radio(
        "color select",
        options=colors,
        format_func=lambda x: "",
        index=2,
        horizontal=True,
        label_visibility="collapsed",
        key="color-selector",
    )

    # css yippee
    st.markdown(f"""
    <style>
        /* 1. HIDE THE EMPTY TEXT LABEL */
        .st-key-color-selector [data-testid="stRadio"] [data-testid="stMarkdownContainer"] {{
            display: none;
        }}

        .st-key-color-selector div[role="radiogroup"] {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            justify-items: center;
            gap: 5px;
        }}
        {
            "".join(
                f'''
                /* Find the label that has the input with this value */
                .st-key-color-selector div[role="radiogroup"] > label:nth-child({i + 1}) > div > div {{
                    background-color: {hex_code};
                    border-color: { "#aaa" if hex_code == "#000000" else hex_code };
                    border-width: 1px;
                    border-style: solid;
                    transition: transform 0.2s;
                }}
                .st-key-color-selector div[role="radiogroup"] > label:nth-child({i + 1}) > div > div:hover {{
                    transform: scale(1.2);
                }}
                '''
            for i, hex_code in enumerate(colors))
        }

    </style>
    """, unsafe_allow_html=True)

    return stroke_color
