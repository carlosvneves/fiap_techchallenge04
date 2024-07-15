
import pandas as pd
import streamlit as st
import utils.prophet_model as prophet_model
import utils.autogluon_model as autogluon_model
from utils.dash_utils import calculate_metrics_for_each_model

import plotly.express as px
import plotly.graph_objects as go


import utils.dash_utils as dash_utils


predictions_autogluon = None
predictions_prophet = None

def display_tabs():

    st.markdown(
        "<h1 style='text-align: center;'> Modelos Preditivos e avaliação das previsões 🔍</h1>", unsafe_allow_html=True
    )


    # build tabs
    tab1, tab2, tab3 = st.tabs(["Prophet", "Autogluon", "Avaliação: Previsão x Observado"])

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
        # horizonte para previsão/teste
        fh = 180
        
        with st.spinner("Carregando o modelo..."):
            model, forecast = prophet_model.prophet_model(fh=fh)

        # previsão para 180 dias
        #st.markdown("""---""")
        
        st.markdown("""---""")      
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Decomposição dos componentes de sazonalidade e tendência:")
            st.plotly_chart(prophet_model.get_forecast_plotly_components(model, forecast))

        with col2:
            st.subheader("Visualização das quebras-estruturais da série temporal:")
            st.pyplot(prophet_model.get_forecast_changepoints(model, forecast), use_container_width=True)

        st.markdown("""---""")

        st.subheader("Métricas da previsão (sem validação cruzada):")
        col1, _ = st.columns(2)
        with col1:
            st.plotly_chart(prophet_model.get_performance_metrics_with_cv_plotly(model))

        st.markdown("""---""")
        st.subheader("Previsão para 180 dias:")
        st.plotly_chart(prophet_model.get_forecast_plotly(model, forecast))

        st.markdown("""---""")
        st.subheader("Métricas de avaliação do modelo:")
        col1,_ = st.columns(2)
        with col1: 
            metrics = prophet_model.get_performance_metrics(forecast, fh=fh)
            metrics = pd.DataFrame(metrics.values(), index=metrics.keys())
            metrics.rename(columns={0: "Performance"}, inplace=True)
            st.table(metrics.map("{:,.2f}".format))
        st.markdown(""" 
    - **MAPE (Mean Absolute Percentage Error)**: Mede a precisão de um modelo de previsão, expressa como uma porcentagem. Um valor de 3.80 indica que, em média, as previsões estão erradas por 3.80% do valor real.
    - **RMSE (Root Mean Squared Error)**: Avalia a diferença entre valores previstos e valores observados. Um valor de 0.67 indica que o desvio padrão das previsões é 0.67 unidades, o que reflete a precisão do modelo.
    - **MSE (Mean Squared Error)**: Mede a média dos quadrados dos erros entre valores previstos e valores observados. Um valor de 15.76 indica que, em média, o quadrado das diferenças entre os valores previstos e os observados é 15.76.
    - **MAE (Mean Absolute Error)**: Avalia a média dos erros absolutos entre valores previstos e valores observados. Um valor de 3.21 indica que, em média, as previsões estão erradas por 3.21 unidades.
    - **MASE (Mean Absolute Scaled Error)**: Compara a precisão de previsões a uma referência, geralmente um modelo simples. Um valor de 7.26 indica que o erro absoluto médio das previsões é 7.26 vezes maior do que o erro absoluto médio da referência.
    - **SMAPE (Symmetric Mean Absolute Percentage Error)**: Mede a precisão das previsões, expressa como uma porcentagem, com ajustes para simetria. Um valor de 3.84 indica que, em média, a diferença entre previsões e valores reais é 3.84% do valor médio das previsões e valores reais.                
                        """)    

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
                - O modelo foi treinado considerando o _preset_: [_chronos large ensemble_](https://auto.gluon.ai/stable/api/autogluon.timeseries.TimeSeriesPredictor.fit.html#autogluon.timeseries.TimeSeriesPredictor.fit);
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
        with st.expander("Importância de cada modelo no _preset chronos large ensemble_"):
            st.markdown("""
                        O _preset chronos large ensemble_ utiliza diversos modelos para realizar as previsões. O _leaderboard_ apresenta os modelos mais importantes para o _ensemble_.
                        """)
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
        col1, _ = st.columns(2)
        with col1:
            st.table(metrics.map("{:,.2f}".format))
        st.markdown("""
    - **MAPE (Mean Absolute Percentage Error)**: Mede a precisão de um modelo de previsão, expressa como uma porcentagem. Um valor de 0.03 indica que, em média, as previsões estão erradas por 0.03% do valor real.
    - **RMSE (Root Mean Squared Error)**: Avalia a diferença entre valores previstos e valores observados. Um valor de 3.39 indica que o desvio padrão das previsões é 3.39 unidades, refletindo a precisão do modelo.
    - **MSE (Mean Squared Error)**: Mede a média dos quadrados dos erros entre valores previstos e valores observados. Um valor de 11.49 indica que, em média, o quadrado das diferenças entre os valores previstos e os observados é 11.49.
    - **MAE (Mean Absolute Error)**: Avalia a média dos erros absolutos entre valores previstos e valores observados. Um valor de 2.51 indica que, em média, as previsões estão erradas por 2.51 unidades.
    - **RMSSE (Root Mean Squared Scaled Error)**: Compara a precisão das previsões em relação a um modelo de referência, geralmente um modelo simples, e mede a raiz do erro quadrático médio escalado. Um valor de 1.18 indica que o erro das previsões é 1.18 vezes maior do que o erro do modelo de referência.
    - **MASE (Mean Absolute Scaled Error)**: Compara a precisão de previsões a uma referência, geralmente um modelo simples. Um valor de 1.14 indica que o erro absoluto médio das previsões é 1.14 vezes maior do que o erro absoluto médio da referência.
    - **SQL (Scaled Quantile Loss)**: Avalia a precisão de previsões baseadas em quantis, escalando o erro de acordo com a distribuição dos dados. Um valor de 1.73 indica a perda média escalada, refletindo a precisão do modelo em prever quantis específicos.            
                    """)
        predictions_autogluon = (
            predictions_out_of_sample.reset_index()[["timestamp", "mean"]]
            .rename(columns={"timestamp": "date", "mean": "yhat_a"})
            .set_index("date")
        )

    with tab3:
        st.header("Comparação da previsão Autogluon e Prophet com os dados observados")

        price_updated = dash_utils.get_price_brent()
        min_date = price_updated.index.min()
        max_date = price_updated.index.max()

        st.markdown(
            f"""
                    ---

                    As previsões fora da amostra foram comparadas com os dados observados entre 11/06/2024 e a última data disponível: {max_date:%d/%m/%Y}.

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
        
        
        st.markdown("""
                    #### Métricas de previsão dos modelos Autogluon e Prophet (11/06/2024 a 01/07/2024).
                    """)   

        col1, _ = st.columns(2)
        with col1:
            st.table(metrics.map("{:,.2f}".format))
        st.divider() 
        st.markdown("""

    - **MSE (Mean Squared Error)**: O modelo Prophet apresenta um MSE de 5.71, significativamente menor do que o MSE de 37.47 do modelo AutoGluon. Isto indica que, em média, os erros quadráticos das previsões do Prophet são menores, sugerindo maior precisão.
    - **RMSE (Root Mean Squared Error)**: O Prophet possui um RMSE de 2.39, enquanto o AutoGluon tem um RMSE de 6.12. RMSE é a raiz quadrada do MSE, então um RMSE menor reflete previsões mais próximas aos valores reais, novamente favorecendo o Prophet.
    - **MAE (Mean Absolute Error)**: O MAE do Prophet é 2.20, comparado ao MAE de 5.40 do AutoGluon. MAE mede a média dos erros absolutos, e um valor menor indica previsões mais precisas em termos absolutos, favorecendo o Prophet.
    - **MAPE (Mean Absolute Percentage Error)**: O Prophet apresenta um MAPE de 2.63%, enquanto o AutoGluon tem um MAPE de 6.29%. O MAPE indica a precisão relativa em termos percentuais, e um valor menor significa que o Prophet tem um erro percentual médio menor, sugerindo maior precisão relativa.

    Com base nas métricas apresentadas:

    - **Prophet** tem um desempenho significativamente melhor em todas as métricas de erro comparadas (MSE, RMSE, MAE, e MAPE).
    - **AutoGluon** apresenta erros substancialmente maiores em todas as métricas, indicando menor precisão nas previsões.

    Ao contrário do resultado considerando os dados de teste e treino, aqui o **modelo Prophet** seria o mais adequado para realizar previsões em um horizonte de até 20 dias, devido ao seu desempenho superior em todas as métricas de erro avaliadas.
            """)