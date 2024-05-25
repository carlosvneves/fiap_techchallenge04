import streamlit as st

# carregamento de bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import ipeadatapy as ip
from os.path import exists
import io
from itables import show



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

st.markdown(
    "<h1 style='text-align: center; color: black;'> Análise Exploratória </h1>",
    unsafe_allow_html=True
)

petr_brent = get_ipea_data()

null_sum = petr_brent['VALUE (US$)'].isnull().sum()
not_null_sum = len(petr_brent) - null_sum



petr_brent = petr_brent.bfill()

df_describe = pd.DataFrame({'Valor':petr_brent.describe()['VALUE (US$)']}).reset_index()
df_describe['index'] = ['Contagem', 'Média', 'Desvio Padrão', 'Mínimo', 'Quantil 25%', 'Mediana', 'Quantil 75%', 'Máximo']

st.markdown("""---""")

_,col01,col02,_ = st.columns(4)
col01.metric(label="Ano de início da série", value = format(petr_brent['YEAR'].min()))
col02.metric(label="Ano de fim da série", value = format(petr_brent['YEAR'].max()))

container = st.container(border=True)

row1 = container.columns(4)
row2 = container.columns(4)

i = 0
for col in row1 + row2:
    col.metric(label= df_describe.loc[i, 'index'], value = format(df_describe.loc[i, 'Valor'], '.2f'))
    i+=1

st.markdown("""---""")
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



from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

df_ds = petr_brent[['DATE','VALUE (US$)']]
df_ds.columns = ['ds','y']

m = Prophet()
m.fit(df_ds)
future = m.make_future_dataframe(periods=180)

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

col1, _,col2 = st.columns(3)

col1.plotly_chart(fig)
container = col2.container(border=True)
with container:
    st.markdown(f"""
    ### Série temporal original
    
    A série de preços históricos do petróleo do tipo _brent_ foi obtida da base do Ipea, por meio de uma API Python: [`ipeadatapy`](https://github.com/luanborelli/ipeadatapy). A API permite que os usuários obtenham dados a partir do código da série temporal. No caso do petróleo do tipo _brent_, a série é a de código __EIA366_PBRENT366__, que é de periodicidade diária, e com início em 2001. 
    É possível verificar a existência de {null_sum} valores _nulos_ de um total de {not_null_sum} na base de dados. Para preencher tais valores, será utilizado o método _ffill()_ da biblioteca _pandas_.

    """)

st.markdown("---")

col1, _, _,col2 = st.columns(4)

col1.plotly_chart(plot_components_plotly(m, forecast))

container = col2.container(border=True)
with container:
    st.markdown(f"""
    ### Decomposição da série nas componentes de tendência, sazonalidade e erro
    
    A série de preços históricos do petróleo do tipo _brent_ foi obtida da base do Ipea, por meio de uma API Python: [`ipeadatapy`](https://github.com/luanborelli/ipeadatapy). A API permite que os usuários obtenham dados a partir do código da série temporal. No caso do petróleo do tipo _brent_, a série é a de código __EIA366_PBRENT366__, que é de periodicidade diária, e com início em 2001. 
    É possível verificar a existência de {null_sum} valores _nulos_ de um total de {not_null_sum} na base de dados. Para preencher tais valores, será utilizado o método _ffill()_ da biblioteca _pandas_.

    """)

st.markdown("""---""")

st.plotly_chart(plot_plotly(m, forecast))

