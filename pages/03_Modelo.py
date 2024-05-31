import streamlit as st

from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.plot import add_changepoints_to_plot

# load data
petr_brent = st.session_state.petr_brent

st.markdown(
    "<h1 style='text-align: center;'> Modelos Preditivos </h1>",
    unsafe_allow_html=True
)

# build tabs
tab1, tab2, tab3 = st.tabs(["Prophet", "Modelo 2", "Modelo 3"])

# prophet model
with tab1:
    st.markdown("""---""")


    df_ds = petr_brent[['DATE','VALUE (US$)']]
    df_ds.columns = ['ds','y']

    #m = Prophet(changepoint_prior_scale=0.5, changepoint_range=0.8)
    # subprime crisis
    cps = ['2006-12-01','2007-02-01','2007-01-01','2008-03-01','2008-09-15', '2008-09-29','2000-03-01',
           '2010-01-01', '2012-01-01','2014-01-01']


    m = Prophet(changepoint_prior_scale=0.5, changepoint_range=0.8, changepoints=cps)
    m.fit(df_ds)

    # six months forecast
    future = m.make_future_dataframe(periods=180)

    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

    container = st.container(border=True)

    container.plotly_chart(plot_components_plotly(m, forecast))

    st.markdown("""---""")

    fig = plot_plotly(m, forecast)

    st.plotly_chart(fig)

    st.markdown("""---""")

    fig = m.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), m, forecast)
    st.pyplot(fig)



