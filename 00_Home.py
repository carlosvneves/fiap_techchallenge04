import streamlit as st
import utils.dash_utils as dash_utils
import locale
import utils.dash_utils as dash_utils

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
dash_utils.output_sidebar()

@st.cache_data
def load_data(): 
    petr_brent = dash_utils.load_data()

    return petr_brent

# Session State also supports attribute based syntax
if 'key' not in st.session_state:
    st.session_state.petr_brent = load_data()

st.markdown("<h1 style='text-align: center'; >Tech Challenge 04</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center'; >MVP de Aplicativo para Análise do Preço do Petróleo do tipo Brent</h2>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center'; >Autor: Carlos Eduardo Veras Neves <br> rm 353068 </h4>", unsafe_allow_html=True)

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.image('images/img_fiap.jpeg', caption='FIAP -Alura Pós-Tech - 3DTAT (julho/2024)', use_column_width=True, width=30)
with col2:
                
    st.page_link("pages/01_Apresentação.py", label="Entendimento do problema de negócio", icon="📊")
    st.page_link("pages/02_Análise_Exploratória.py", label="Tratamento dos dados (_data cleaning_)", icon="🛠️")
    st.page_link("pages/02_Análise_Exploratória.py", label="Análise exploratória dos dados", icon="🔍")
    st.page_link("pages/03_Modelos.py", label="Avaliação do modelo preditivo", icon="📈")
    st.page_link("pages/04_Conclusão.py", label="Conclusão (ou _insights_)", icon="💡")


