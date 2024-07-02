import pandas as pd
import streamlit as st
import utils.prophet_model as prophet_model
import utils.autogluon_model as autogluon_model

import plotly.express as px
import plotly.graph_objects as go

# load data
# petr_brent = st.session_state.petr_brent

st.markdown(
    "<h1 style='text-align: center;'> Modelos Preditivos </h1>", unsafe_allow_html=True
)

# build tabs
tab1, tab2, tab3 = st.tabs(
    ["Prophet", "Autogluon - Multivariado", "XGBoost - Multivariado"]
)

# prophet model
with tab1:
    # previsão para 180 dias
    st.markdown("""---""")

    model, forecast = prophet_model.prophet_model()

    st.plotly_chart(prophet_model.get_forecast_plotly(model, forecast))

    st.markdown("""---""")

    st.plotly_chart(prophet_model.get_forecast_plotly_components(model, forecast))

    st.markdown("""---""")

    st.pyplot(prophet_model.get_forecast_changepoints(model, forecast))


with tab2:

    with st.spinner("Carregando o modelo..."):
        predictor, df_mult_train, df_mult_test = autogluon_model.autogluon_model(
            load=True
        )
    # insample predictions
    with st.spinner("Realizando as previsões (dentro da amostra)..."):
        predictions = autogluon_model.predict(
            df_mult_train, known_covariates=df_mult_test, predictor=predictor
        )

    st.markdown("## Previsões (dentro da amostra - 180 dias):")

    st.plotly_chart(
        autogluon_model.get_forecast_plotly(
            test_data=df_mult_test, predictions=predictions
        )
    )

    st.markdown("### Importância de cada modelo no _ensemble_:")
    
    st.write(predictor.fit_summary().get("leaderboard"))

    st.markdown("### Métricas de avaliação do modelo:")

    metrics = predictor.evaluate(
            df_mult_test, metrics=["MAPE", "RMSE", "MSE", "MAE", "RMSSE", "MASE", "SQL"]
        )
    metrics = pd.DataFrame(metrics.values(), index=metrics.keys())
    st.write(
        metrics
    )

    st.markdown("## Previsão (fora da amostra - 180 dias):")

    future_data = autogluon_model.make_future_data(df_mult_test, fh=180)

    predictions_out_of_sample = autogluon_model.predict(
        df_mult_test, known_covariates=future_data, predictor=predictor
    )

    # st.write(predictions_out_of_sample)

    st.plotly_chart(
        autogluon_model.get_forecast_plotly(
            test_data=df_mult_test, predictions=predictions_out_of_sample
        )
    )

with tab3:
    st.write("XGBoost - Multivariado")
