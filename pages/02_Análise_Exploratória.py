import streamlit as st

# carregamento de bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import ipeadatapy as ip


@st.cache_data
def get_ipea_data():
    # baixa os dados do site do ipea
    ip_metadata = ip.metadata()

    # busca do código da série de Preço - petróleo bruto - Brent (FOB)
    ip_metadata[ip_metadata["NAME"].str.contains("Brent") == True]

    # seleção da série com dados a partir de 2001
    petr_brent = ip.timeseries("EIA366_PBRENT366", yearGreaterThan=2001)

    return petr_brent


st.markdown(
    "<h1 style='text-align: center; color: white;'> Análise Exploratória </h1>",
    unsafe_allow_html=True,
)


st.markdown(""" ## Obtenção dos dados

A série de preços históricos do petróleo do tipo _brent_ foi obtida da base do Ipea, por meio de uma API Python: [`ipeadatapy`](https://github.com/luanborelli/ipeadatapy). A API permite que os usuários obtenham dados a partir do código da série temporal. No caso do petróleo do tipo _brent_, a série é a de código __EIA366_PBRENT366__, que é de periodicidade diária, e com início em 2001. 
""")

petr_brent = get_ipea_data()

st.markdown(""" 

A estatísticas descritivas da série de preços do petroleo Brent podem ser observadas a seguir:
""")

st.dataframe(pd.DataFrame(petr_brent.describe()['VALUE (US$)']))


st.markdown(""" 

É possível verificar a existência de valores _nulos_ na base de dados, 
""")


st.markdown("""

## Visualização dos dados

""")


# gráfico da série temporal
fig = px.line(
    petr_brent,
    x="RAW DATE",
    y="VALUE (US$)",
)

fig.update_layout(
    title="Preços do petroleo Brent",
    xaxis_title="Data",
    yaxis_title="Preço (US$)",
)

st.plotly_chart(fig)
