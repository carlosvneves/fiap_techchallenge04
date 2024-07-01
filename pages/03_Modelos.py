import pandas as pd
import streamlit as st
import utils.prophet_model as prophet_model
import utils.autogluon_model as autogluon_model

# load data
petr_brent = st.session_state.petr_brent

st.markdown(
    "<h1 style='text-align: center;'> Modelos Preditivos </h1>",
    unsafe_allow_html=True
)

# build tabs
tab1, tab2, tab3 = st.tabs(["Prophet", "Autogluon - Multivariado", "XGBoost - Multivariado"])

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
    import matplotlib.pyplot as plt 
    
    st.write("Autogluon - Multivariado")

    with st.spinner("Carregando o modelo..."):
        predictor, df_mult_train, df_mult_test = autogluon_model.autogluon_model(load=True)
    # insample predictions
    with st.spinner("Realizando as previsões (dentro da amostra)..."):
        predictions = autogluon_model.predict(df_mult_train, known_covariates=df_mult_test, predictor=predictor)
    st.write(predictions)
     
    # fig, ax = plt.figure(figsize=(10, 9))
    # autogluon_model.get_forecast_chart(df_mult_test, predictions, predictor)

    st.pyplot(autogluon_model.get_forecast_chart(df_mult_test, predictions, predictor), )
        

with tab3:
    st.write("XGBoost - Multivariado")
