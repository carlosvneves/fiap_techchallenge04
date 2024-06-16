import streamlit as st
import utils.dash_utils as dash_utils

@st.cache_data
def load_data(): 
    petr_brent = dash_utils.load_data()

    return petr_brent

# Session State also supports attribute based syntax
if 'key' not in st.session_state:
    st.session_state.petr_brent = load_data()

st.markdown("<h1 style='text-align: center'; >Tech Challenge 04</h1>", unsafe_allow_html=True)

st.image('images/img_fiap.jpeg', caption='FIAP -Alura Pós-Tech - 3DTAT (maio/2024)', use_column_width=True)

st.markdown("""
            ## Análise da série de Preços do Petróleo do tipo Brent
            ---

            ### Elaborado por:
            - Carlos Eduardo Veras Neves - rm 353068

            """)
