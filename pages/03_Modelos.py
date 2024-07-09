import pandas as pd
import streamlit as st
import utils.prophet_model as prophet_model
import utils.autogluon_model as autogluon_model
from utils.dash_utils import calculate_metrics_for_each_model

import plotly.express as px
import plotly.graph_objects as go


# pd.options.display.float_format = "{:,.2f}".format

@st.cache_data
def get_preco_brent():
    import ipeadatapy as ip

    petr_brent = ip.timeseries("EIA366_PBRENT366", yearGreaterThan=2023).reset_index()
    petr_brent = petr_brent[["DATE", "VALUE (US$)"]].rename(
        columns={"DATE": "date", "VALUE (US$)": "price"}
    )
    petr_brent["date"] = pd.to_datetime(petr_brent["date"])

    petr_brent.query('date >= "2024-06-01"', inplace=True)
    petr_brent.set_index("date", inplace=True)

    return petr_brent


predictions_autogluon = None
predictions_prophet = None

st.markdown(
    "<h1 style='text-align: center;'> Modelos Preditivos </h1>", unsafe_allow_html=True
)

# build tabs
tab1, tab2, tab3 = st.tabs(["Prophet", "Autogluon", "Comparação com o observado"])

# prophet model
with tab1:
    st.header("Previsão Prophet ")
    with st.expander("Sobre o modelo"):
        st.markdown(
            """
            O modelo foi construído considerando:
            - Biblioteca [_prophet_](https://facebook.github.io/prophet/);
            - Dados da série temporal de petróleo do tipo _brent_ entre 2001 e 2024;
            - Foram incluídos _changepoints_ relativos à crise do Subprime (2008-2010),
            o colapso do preço do petróleo (2014 a 2016) e a Pandemia de Covid-19 (2020 a 2022);
            - Previsão para 180 dias (fora da amostra).

            """
        )

    with st.spinner("Carregando o modelo..."):
        model, forecast = prophet_model.prophet_model()

    # previsão para 180 dias
    st.markdown("""---""")
    # st.markdown("## Decomposição nos componentes de sazonalidade e tendência:")
    st.subheader("Decomposição dos componentes de sazonalidade e tendência:")
    st.plotly_chart(prophet_model.get_forecast_plotly_components(model, forecast))

    st.markdown("""---""")

    st.subheader("Visualização das quebras-estruturais da série temporal:")
    st.pyplot(prophet_model.get_forecast_changepoints(model, forecast))

    st.markdown("""---""")

    st.subheader("Métricas da previsão (sem validação cruzada):")

    st.plotly_chart(prophet_model.get_performance_metrics_with_cv_plotly(model))

    st.markdown("""---""")
    st.subheader("Previsão para 180 dias:")
    st.plotly_chart(prophet_model.get_forecast_plotly(model, forecast))

    st.markdown("""---""")
    st.subheader("Métricas de avaliação do modelo:")
    metrics = prophet_model.get_performance_metrics(forecast)
    metrics = pd.DataFrame(metrics.values(), index=metrics.keys())
    metrics.rename(columns={0: "Performance"}, inplace=True)
    st.table(metrics.map("{:,.2f}".format))

    predictions_prophet = (
        forecast.copy()[["ds", "yhat"]]
        .rename(columns={"ds": "date", "yhat": "yhat_p"})
        .query('date >= "2024-06-01"')
        .set_index("date")
    )

with tab2:
    st.header("Previsão Autogluon ")
    with st.expander("Sobre o modelo"):
        st.markdown(
            """
            O modelo foi construído considerando:
            - Biblioteca [_autogluon_](auto.gluon.ai);
            - Dados da série temporal de petróleo do tipo _brent_ entre 2001 e 2024;
            - O modelo é multivariado e considera as seguintes _features_:
                - Componentes sazonais: mês, dia da semana;
                - Componentes de calendário: ano, trimestre, dia do ano;
            - O modelo foi treinado considerando o _preset_: [_chronos_large_ensemble_](https://auto.gluon.ai/stable/api/autogluon.timeseries.TimeSeriesPredictor.fit.html#autogluon.timeseries.TimeSeriesPredictor.fit);
            - A métrica de treinamento é a _WQL_ (Weighted Quantile Loss), baseada em quantis e com uma abordagem probabilística de previsão;


        """
        )

    st.markdown("---")

    with st.spinner("Carregando o modelo..."):
        predictor, df_mult_train, df_mult_test = autogluon_model.autogluon_model(
            load=True
        )
        predictions = autogluon_model.predict(
            df_mult_train, known_covariates=df_mult_test, predictor=predictor
        )

    st.subheader("Previsão para 180 dias (dentro da amostra):")
    st.plotly_chart(
        autogluon_model.get_forecast_plotly(
            test_data=df_mult_test, predictions=predictions
        )
    )

    st.markdown("""---""")
    st.subheader("Importância de cada modelo no _ensemble_:")

    st.table(predictor.fit_summary().get("leaderboard"))

    st.markdown("""---""")
    st.subheader("Previsão para 180 dias (fora da amostra):")

    future_data = autogluon_model.make_future_data(df_mult_test, fh=180)

    predictions_out_of_sample = autogluon_model.predict(
        df_mult_test, known_covariates=future_data, predictor=predictor
    )

    st.plotly_chart(
        autogluon_model.get_forecast_plotly(
            test_data=df_mult_test, predictions=predictions_out_of_sample
        )
    )

    st.markdown("""---""")
    st.subheader("Métricas de avaliação do modelo:")
    metrics = predictor.evaluate(
        df_mult_test, metrics=["MAPE", "RMSE", "MSE", "MAE", "RMSSE", "MASE", "SQL"]
    )
    metrics = pd.DataFrame(metrics.values(), index=metrics.keys())
    metrics = -1 * metrics
    metrics.rename(columns={0: "Performance"}, inplace=True)
    st.table(metrics.map("{:,.2f}".format))

    predictions_autogluon = (
        predictions_out_of_sample.reset_index()[["timestamp", "mean"]]
        .rename(columns={"timestamp": "date", "mean": "yhat_a"})
        .set_index("date")
    )

with tab3:
    st.header("Comparação da previsão Autogluon e Prophet com os dados observados")

    price_updated = get_preco_brent()
    min_date = price_updated.index.min()
    max_date = price_updated.index.max()

    st.markdown(
        f"""
                ---

                As previsões fora da amostra foram comparadas com os dados observados entre 01/06/2024 e a última data disponível: {max_date:%d/%m/%Y}.

                A seguir está gráfico com os dados observados e as previsões para o modelo Autogluon e o modelo Prophet. A tabela mostra
                as métricas de avaliação dos modelos.

                """
    )


    fig = go.Figure()

    df_merge = pd.merge(
        price_updated.reset_index(),
        predictions_autogluon.reset_index(),
        on="date",
        how="inner",
    )

    df_merge = pd.merge(
        df_merge, predictions_prophet.reset_index(), on="date", how="inner"
    )

    fig.add_trace(
        go.Scatter(
            x=df_merge["date"],
            y=df_merge["price"],
            mode="lines",
            name="Original",
            opacity=0.3,
            marker=dict(color="black"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_merge["date"],
            y=df_merge["yhat_a"],
            mode="lines",
            name="Autogluon",
            line=dict(color="royalblue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_merge["date"],
            y=df_merge["yhat_p"],
            mode="lines",
            name="Prophet",
            line=dict(color="red"),
        )
    )

    st.plotly_chart(fig)

    metrics = calculate_metrics_for_each_model(df_merge)

    metrics = pd.DataFrame(metrics.values(), index=metrics.keys()).T
    metrics.rename(columns={"yhat_a": "Autogluon", "yhat_p": "Prophet"}, inplace=True)

    st.table(metrics.map("{:,.2f}".format))
