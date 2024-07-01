# Prophet Model
import pandas as pd

from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.plot import add_changepoints_to_plot

def prepare_input():
    anomalize_df = pd.read_csv('data/anomalyze_df.csv')
    df_ds = anomalize_df[['date','observed_clean']]#pd.read_csv('data/price.csv').drop(axis=1, columns=['Unnamed: 0']) #petr_brent[['DATE','VALUE (US$)']]
    df_ds.columns = ['ds','y']
    
    return df_ds

def predict(model, fh=180):
    
    # six months forecast
    future = model.make_future_dataframe(periods=fh)

    forecast = model.predict(future)
    #forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return forecast

def get_forecast_changepoints(model, forecast):
    
    fig = model.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), model, forecast)
    
    return fig
    
def get_forecast_plotly_components(model, forecast):
    fig = plot_components_plotly(model, forecast)
    return fig

def get_forecast_plotly(model, forecast):
    fig = plot_plotly(model, forecast)
    return fig
    
    
def prophet_model(fh=180):

    df_ds = prepare_input()

    # subprime crisis
    cps = ['2006-12-01','2007-02-01','2008-03-01','2008-09-15', '2008-09-29','2001-03-01',
           '2010-01-01', '2012-01-01','2014-01-01', '2016-01-01', '2018-01-01', '2020-03-01','2021-06-01',
           '2022-02-22', '2023-03-01', '2023-12-01']


    m = Prophet(changepoint_prior_scale=0.1, changepoint_range=0.8, changepoints=cps)
    m.fit(df_ds)

    forecast = predict(m,fh)

    return m,forecast
