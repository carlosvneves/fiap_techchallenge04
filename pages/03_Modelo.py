import streamlit as st

from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

# load data
petr_brent = st.session_state.petr_brent

st.markdown(
    "<h1 style='text-align: center; color: black;'> Modelos Preditivos </h1>",
    unsafe_allow_html=True
)

# build tabs
tab1, tab2, tab3 = st.tabs(["Prophet", "Modelo 2", "Modelo 3"])

# prophet model
with tab1:
    st.markdown("""---""")


    df_ds = petr_brent[['DATE','VALUE (US$)']]
    df_ds.columns = ['ds','y']

    m = Prophet()
    m.fit(df_ds)
    future = m.make_future_dataframe(periods=180)

    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

    container = st.container(border=True)

    container.plotly_chart(plot_components_plotly(m, forecast))

    st.markdown("""---""")

    st.plotly_chart(plot_plotly(m, forecast))
