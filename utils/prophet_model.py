# Prophet Model
import pandas as pd

from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.plot import add_changepoints_to_plot
from prophet.diagnostics import performance_metrics
from prophet.diagnostics import cross_validation
from prophet.serialize import model_to_json, model_from_json

from os import path
import plotly.graph_objects as go

from sklearn.metrics import mean_squared_error, mean_absolute_error
# import numpy as np


def prepare_input():
    anomalize_df = pd.read_csv("data/anomalyze_df.csv")
    df_ds = anomalize_df[
        ["date", "observed_clean"]
    ]  # pd.read_csv('data/price.csv').drop(axis=1, columns=['Unnamed: 0']) #petr_brent[['DATE','VALUE (US$)']]
    df_ds.columns = ["ds", "y"]

    return df_ds


def predict(model, fh=180):

    # six months forecast
    future = model.make_future_dataframe(periods=fh)

    forecast = model.predict(future)
    # forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return forecast


def get_forecast_changepoints(model, forecast):

    fig = model.plot(forecast)
    add_changepoints_to_plot(fig.gca(), model, forecast)

    return fig


def get_forecast_plotly_components(model, forecast):
    fig = plot_components_plotly(model, forecast)
    return fig


def get_forecast_plotly(model, forecast):
    fig = plot_plotly(model, forecast)
    return fig


def get_performance_metrics_with_cv(model):

    if not path.exists("saved_models/prophet/performance_metrics.csv"):
        df_cv = cross_validation(
            model, initial="900 days", period="300 days", horizon="180 days"
        )
        df_p = performance_metrics(df_cv)
        df_p.to_csv("saved_models/prophet/performance_metrics.csv")
    else:
        df_p = pd.read_csv("saved_models/prophet/performance_metrics.csv")

    return df_p


def get_performance_metrics_with_cv_plotly(model):
    data = get_performance_metrics_with_cv(model)
    horizon = data["horizon"]
    metrics = ["mse", "rmse", "mae", "mape", "mdape", "smape"]

    # Min-max normalization for the error metrics
    normalized_data = data.copy()
    for metric in metrics:
        min_value = data[metric].min()
        max_value = data[metric].max()
        normalized_data[metric] = (data[metric] - min_value) / (max_value - min_value)

    # Create a bar plot with normalized metrics
    fig_normalized = go.Figure()

    # Add bars for each normalized metric
    for metric in metrics:
        fig_normalized.add_trace(
            go.Bar(x=horizon, y=normalized_data[metric], name=metric)
        )

    # Update the layout of the plot
    fig_normalized.update_layout(
        title="Normalized Error Metrics vs Horizon",
        xaxis_title="Horizon",
        yaxis_title="Normalized Error Metrics",
        barmode="group",
    )

    return fig_normalized


def get_performance_metrics(forecast, fh=180):
    df = prepare_input()
    df["ds"] = pd.to_datetime(df["ds"])
    forecast["ds"] = pd.to_datetime(forecast["ds"])

    # Merge actual values and predicted values
    results = pd.merge(df, forecast[["ds", "yhat"]], on="ds", how="left")

    # Slice the results to get only the last 180 days (in-sample)
    results = results[-fh:]

    # Actual values
    y_true = results["y"]

    # Predicted values
    y_pred = results["yhat"]

    # Calculate RMSE
    rmse = mean_squared_error(y_true, y_pred, squared=False)

    # Calculate MAE
    mae = mean_absolute_error(y_true, y_pred)

    # Calculate MAPE
    mape = (abs((y_true - y_pred) / y_true).mean()) * 100

    # Calculate SMAPE
    smape = (abs(y_true - y_pred) / ((abs(y_true) + abs(y_pred)) / 2)).mean() * 100

    # Calculate MSE
    mse = mean_squared_error(y_true, y_pred)

    # Calculate MASE
    # Naive forecast (previous value)
    naive_forecast = y_true.shift(1)
    naive_forecast[0] = 0  # np.nan  # The first value is undefined
    naive_mae = mean_absolute_error(y_true, naive_forecast[1:])
    mase = mae / naive_mae

    # Calculate RMSSE
    naive_rmse = mean_squared_error(y_true, naive_forecast[1:], squared=False)
    rmsse = rmse / naive_rmse

    metrics = {
        "MAPE": mape,
        "RMSE": rmse,
        "MSE": mse,
        "MAE": mae,
        "RMSE": rmsse,
        "MASE": mase,
        "SMAPE": smape,
    }

    return metrics 

def prophet_model(fh=180, load=True):

    if not load or not path.exists("saved_models/prophet/serialized_model.json"):
        with open("saved_models/prophet/serialized_model.json", "w") as fout:
            # subprime crisis
            cps = [
                "2006-12-01",
                "2007-02-01",
                "2008-03-01",
                "2008-09-15",
                "2008-09-29",
                "2010-01-01",
                "2012-01-01",
                "2014-01-01",
                "2016-01-01",
                "2018-01-01",
                "2020-03-01",
                "2021-06-01",
                "2022-02-22",
                "2023-03-01",
                "2023-12-01",
            ]
            df_ds = prepare_input()

            m = Prophet(
                changepoint_prior_scale=0.1, changepoint_range=0.8, changepoints=cps
            )
            m.fit(df_ds)
            fout.write(model_to_json(m))  # Save model
    else:
        with open("saved_models/prophet/serialized_model.json", "r") as fin:
            m = model_from_json(fin.read())  # Load model

    forecast = predict(m, fh)

    return m, forecast
