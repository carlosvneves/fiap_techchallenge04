# carregamento de bibliotecas
import streamlit as st
import pandas as pd
import pytimetk as tk
# import numpy as np
# import matplotlib.pyplot as plt
import plotly.express as px
# import io

# Begin
st.markdown(
    "<h1 style='text-align: center;'> Análise Exploratória </h1>",
    unsafe_allow_html=True
)

# load data
petr_brent = st.session_state.petr_brent

# convert RAW DATE to datetime
petr_brent['DATE'] = pd.to_datetime(petr_brent['DATE'])

tab1, tab2 = st.tabs(["Petróleo Brent", "Fatores Exógenos"])


# calculate descriptive statistics

# calculate null values
null_sum = petr_brent['VALUE (US$)'].isnull().sum()
not_null_sum = len(petr_brent) - null_sum

petr_brent = petr_brent.bfill()

df_describe = pd.DataFrame({'Valor':petr_brent.describe()['VALUE (US$)']}).reset_index()
df_describe['index'] = ['Contagem', 'Média', 'Desvio Padrão', 'Mínimo', 'Quantil 25%', 'Mediana', 'Quantil 75%', 'Máximo']

st.markdown("""---""")
# Display descriptive statistics on screen

# year of beginning and end
_ ,col01, col02,_ = st.columns(4)
col01.metric(label="Ano de início da série", value = format(petr_brent['YEAR'].min()))
col02.metric(label="Ano de fim da série", value = format(petr_brent['YEAR'].max()))

container = st.container(border=True)

row1 = container.columns(4)
row2 = container.columns(4)

i = 0
for col in row1 + row2:
    col.metric(label= df_describe.loc[i, 'index'], value = format(df_describe.loc[i, 'Valor'], '.2f'))
    i += 1

st.markdown("""---""")

container = st.container(border=True)

# Original time series chart
fig = px.line(
    petr_brent,
    x="DATE",
    y="VALUE (US$)",
)

fig.update_layout(
    title="Preços do petroleo Brent",
    xaxis_title="Data",
    yaxis_title="Preço (US$)",
)



with container:
    st.markdown(f"""
    ### Série temporal original

    <p style="text-align: justify">A série de preços históricos do petróleo do tipo <b>brent</b> foi obtida da base do Ipea, por meio de uma API Python: 
    <a href="https://github.com/luanborelli/ipeadatapy">[`ipeadatapy`]</a>. A API permite que os usuários obtenham dados a partir do 
    código da série temporal. No caso do petróleo do tipo <b>brent</b>, a série é a de código <b>EIA366_PBRENT366</b>, que é de 
    periodicidade diária, e com início em 2001.
    É possível verificar a existência de {null_sum} valores <i>nulos</i> de um total de {not_null_sum} na base de dados.
    Para preencher tais valores, será utilizado o método <i>ffill()</i> da biblioteca <i>pandas</i>.

    </p>

    """, unsafe_allow_html=True
)

container.plotly_chart(fig)

st.markdown("---")


# Seasonal Decomposition
container = st.container(border=True)

container.write("""
    ### Decomposição da série em suas componentes de tendência, sazonalidade e erro.

    <p style="text-align: justify">
    A decomposição permite verificar qual o tipo de processo gerador da séries temporal e, consequentemente, qual o 
    tipo de modelo pode ser mais adequado para compreender a série e realizar previsões.
    No caso, a série não é estacionária, logo, <b>deverá ser realizado um trabalho de tratamento da série 
    para facilitar a construção de um modelo preditivo</b>.
    </p>


""", unsafe_allow_html=True)

anomalize_df = tk.anomalize(
    data          = petr_brent,
    date_column   = 'DATE',
    value_column  = 'VALUE (US$)',
    period        = 7,
    iqr_alpha     = 0.05, # using the default
    clean_alpha   = 0.75, # using the default
    clean         = "min_max"
)

# Plot seasonal decomposition
container.plotly_chart(
    tk.plot_anomalies_decomp(
    data        = anomalize_df,
    date_column = 'DATE',
    engine      = 'plotly',
    title       = 'Seasonal Decomposition'
)
)

st.markdown("---")

# Anomalies detection
container = st.container(border=True)

with container:
    st.markdown(f"""
    ### Detecção de Anomalias

    <p style="text-align: justify">A série de preços históricos do petróleo do tipo <b>brent</b> foi obtida da base do Ipea, por meio de uma API Python: 
    <a href="https://github.com/luanborelli/ipeadatapy">[`ipeadatapy`]</a>. A API permite que os usuários obtenham dados a partir do 
    código da série temporal. No caso do petróleo do tipo <b>brent</b>, a série é a de código <b>EIA366_PBRENT366</b>, que é de 
    periodicidade diária, e com início em 2001.
    É possível verificar a existência de {null_sum} valores <i>nulos</i> de um total de {not_null_sum} na base de dados.
    Para preencher tais valores, será utilizado o método <i>ffill()</i> da biblioteca <i>pandas</i>.

    </p>

    """, unsafe_allow_html=True
)


# Plot anomalies
container.plotly_chart(
    tk.plot_anomalies(
    data        = anomalize_df,
    date_column = 'DATE',
    engine      = 'plotly',
    title       = 'Anomalias Detectadas'
)
)

# Plot cleaned anomalies
container.plotly_chart(
    tk.plot_anomalies_cleaned(
    data        = anomalize_df,
    date_column = 'DATE',
    engine      = 'plotly',
    title       = 'Série após o Processo de "limpeza" de anomalias'
)
)
