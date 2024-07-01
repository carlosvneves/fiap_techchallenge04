import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
from autogluon.timeseries.utils.forecast import get_forecast_horizon_index_ts_dataframe

from os import path

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
        eval_metric="SQL",
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
        presets="fast_training", #"hq",
        time_limit=600,
        num_val_windows=5,
        random_seed=123,
    )

    #predictions = predictor.predict(train_data, known_covariates=test_data)

    return predictor

def predict(data, known_covariates, predictor, fh=180):
    return predictor.predict(data, known_covariates=known_covariates)

def make_future_data(data, fh=180):
    
    future_index = get_forecast_horizon_index_ts_dataframe(data, prediction_length=fh)
    known_covariates = pd.DataFrame(index=future_index)

    return known_covariates


def load_predictor(path="saved_models/autogluon-petr-mult"):
    predictor = TimeSeriesPredictor.load(path)
    return predictor
    
def get_forecast_chart(data, predictions, predictor):
    
   return predictor.plot(data, predictions=predictions, quantile_levels=[0.1, 0.5, 0.9],)


def autogluon_model(fh=180, load=False):
    
    fh = 180
     
    data = prepare_input()

    df_mult_train, df_mult_test = data.train_test_split(prediction_length=fh)
    
    if  not load or not path.exists("saved_models/autogluon-petr-mult"): 
        predictor = fit_and_test(df_mult_train, df_mult_test, fh)
    else :
        predictor = load_predictor()
    
    return predictor, df_mult_train, df_mult_test
    

    
    
if __name__ == "__main__":
    predictor, df_mult_train, df_mult_test = autogluon_model()
    # insample predictions
    predictions = predict(df_mult_train, known_covariates=df_mult_test, predictor=predictor)
    print(predictions.head())
    get_forecast_chart(df_mult_test, predictions, predictor)