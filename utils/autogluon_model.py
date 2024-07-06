import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
from autogluon.timeseries.utils.forecast import get_forecast_horizon_index_ts_dataframe

from os import path


import plotly.graph_objects as go

# implementar outras features como aqui?
# https://plbalmeida.gitbook.io/fiap-hands-on-de-ml-para-series-temporais/parte-1/overview/previsao-de-preco-d+15/performance_ml_d7

#def set_predictions_prophet():
    
#predictions_prophet: pd.DataFrame = [] 
#predictions_autogluon: pd.DataFrame = []


def create_features(df):
    """
    Create time series features based on time series index.
    """
    df = df.copy()
    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.day_of_week
    df["quarter"] = df.index.quarter
    df["month"] = df.index.month
    df["year"] = df.index.year
    df["dayofyear"] = df.index.day_of_year
    #df["rolling_std_7"] = df["y"].shift(1).rolling(window=7).std()
    return df.reset_index()


def prepare_input():

    anomalize_df = pd.read_csv("data/anomalyze_df.csv")
    data = anomalize_df[["date", "observed_clean"]].copy()
    data['date'] = data['date'].astype('datetime64[ns]')
    data.rename(columns={"observed_clean": "y"}, inplace=True)
    data.set_index("date", inplace=True)


    data = create_features(data)

    data["item_id"] = "petr_brent"

    data = TimeSeriesDataFrame(data, id_column="item_id", 
                                timestamp_column="date"
                                )
    return data


def fit_and_test(train_data, test_data, fh=180):

    
    predictor = TimeSeriesPredictor(
        prediction_length=fh,
        path="saved_models/autogluon-petr-mult",
        target="y",
        eval_metric= "wQL",
        quantile_levels=[0.1, 0.25, 0.5, 0.75, 0.9],
        known_covariates_names=[
            "hour",
            "dayofweek",
            "quarter",
            "month",
            "year",
            "dayofyear",
        ],
    )

    predictor.fit(
        train_data,
        #presets="hq", # caso não tenha gpu para treinar o modelo
        presets= "chronos_large_ensemble",        
        time_limit=600,
        num_val_windows=5,
        random_seed=123,
        
    )

    return predictor

def predict(data, known_covariates, predictor, fh=180):
    return predictor.predict(data, known_covariates=known_covariates)

def make_future_data(data, fh=180):
    
    future_index = get_forecast_horizon_index_ts_dataframe(data, prediction_length=fh)
    future_timestamps = future_index.get_level_values("timestamp")
    known_covariates = pd.DataFrame(index=future_index)
    known_covariates['hour'] = future_timestamps.hour
    known_covariates['dayofweek'] = future_timestamps.day_of_week
    known_covariates['quarter'] = future_timestamps.quarter
    known_covariates['month'] = future_timestamps.month
    known_covariates['year'] = future_timestamps.year
    known_covariates['dayofyear'] = future_timestamps.day_of_year


    return known_covariates


def load_predictor(path="saved_models/autogluon-petr-mult"):
    predictor = TimeSeriesPredictor.load(path)
    return predictor
    
def get_forecast_chart(data, predictions, predictor):
    
   return predictor.plot(data, predictions=predictions, quantile_levels=[0.1, 0.5, 0.9],)


def get_forecast_plotly(test_data, predictions):

    fig = go.Figure()

    df_merge = pd.merge(
        test_data, predictions.reset_index(), on="timestamp", how="outer"
    )

    # Add original values as a scatter plot
    fig.add_trace(
        go.Scatter(
            x=df_merge["timestamp"],
            y=df_merge["y"],
            mode="lines",
            name="Original",
            opacity=0.3,
            marker=dict(color="black"),
        )
    )
    # Add the predicted mean line
    fig.add_trace(
        go.Scatter(
            x=df_merge["timestamp"],
            y=df_merge["mean"],
            mode="lines",
            name="Média da Previsão",
            line=dict(color="royalblue"),
        )
    )
    # Add the lower quantile trace using Plotly Graph Objects
    fig.add_trace(
        go.Scatter(
            x=df_merge["timestamp"],
            y=df_merge["0.1"],
            mode="lines",
            name="Q10",
            line=dict(width=0),
            showlegend=False,
        )
    )

    # Add the upper quantile trace and fill the area between the quantiles using Plotly Graph Objects
    fig.add_trace(
        go.Scatter(
            x=df_merge["timestamp"],
            y=df_merge["0.9"],
            mode="lines",
            name="Q90",
            fill="tonexty",  # fill area between quant_0.1 and quant_0.9
            fillcolor="rgba(255,165,0,0.2)",
            line=dict(width=0),
            showlegend=False,
        )
    )

    # Set the initial x-axis range to start on 2022-06-01
    fig.update_xaxes(
        range=["2022-01-01", df_merge.reset_index()["timestamp"].max()]
    )

    # Update layout for better presentation
    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Value US$",
        title="Previsão do preço de petróleo do tipo brent",
        template="plotly_white",
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(
                visible=True,
                range=[
                    df_merge.reset_index()["timestamp"],
                    df_merge.reset_index()["timestamp"].max(),
                ],
            ),
            type="date",
        ),
        width=900,  # Set the width of the figure
        height=800,  # Set the height of the figure
    )
    return fig 

    
def autogluon_model(fh=180, load=False):
    
    fh = 180
     
    data = prepare_input()

    df_mult_train, df_mult_test = data.train_test_split(prediction_length=fh)
    
    if  not load or not path.exists("saved_models/autogluon-petr-mult"): 
        predictor = fit_and_test(df_mult_train, df_mult_test, fh)
    else :
        predictor = load_predictor()
    
    return predictor, df_mult_train, df_mult_test