import streamlit as st
import ipeadatapy as ip
from os.path import exists
import pandas as pd

@st.cache_data
def get_ipea_data():
    if not exists('data/petr_brent.csv'):

        # baixa os dados do site do ipea
        #ip_metadata = ip.metadata()
        # busca do código da série de Preço - petróleo bruto - Brent (FOB)
        #ip_metadata[ip_metadata["NAME"].str.contains("Brent") == True]

        # seleção da série com dados a partir de 2001
        petr_brent = ip.timeseries("EIA366_PBRENT366", yearGreaterThan=2001)
        petr_brent.to_csv('data/petr_brent.csv')
    else:
        petr_brent = pd.read_csv('data/petr_brent.csv')

    return petr_brent


# Session State also supports attribute based syntax
if 'key' not in st.session_state:
    st.session_state.petr_brent = get_ipea_data()

st.markdown("<h1 style='text-align: center'; >Tech Challenge 04</h1>", unsafe_allow_html=True)

st.image('images/img_fiap.jpeg', caption='FIAP -Alura Pós-Tech - 3DTAT (maio/2024)', use_column_width=True)

st.markdown("""
            ## Análise da série de Preços do Petróleo do tipo Brent
            ---

            ### Elaborado por:
            - Carlos Eduardo Veras Neves - rm 353068

            """)
