import streamlit as st
import pandas as pd

import utils.dash_utils as dash_utils

dash_utils.output_sidebar()

st.title("Insights💡")


st.subheader("Principais pontos de observação:")
st.markdown("""
            <p style="text-align: justify">

            - O preço do petróleo do tipo _brent_ foi estudado considerando uma série de 8562 valores, de 2021 a 2024;
            
            - Os valores máximo e mínimo no período foram, respectivamente, US\$ 143,95 (julho/2008) e US\$ 9,12 (abril/2020), respectivamente;
            
            - Eventos como a crise do subprime (2007 a 2010), a Primavera Árabe (2010~), o colapso do petroleo (2014 a 2016), a Pandemia de Covid-19 (2020 a 2022),
            Conflito Rússia-Ucrânia (2022~), impactaram o valor do petroleo do tipo _brent_;
            
            - Apesar de haver correlação entre preço, oferta e demanda, em geral, não foram encontradas relações causais no sentido _Granger_
            considerando as proxies escolhidas para os testes de causalidade;
            
            - A única exceção à observação anterior ocorreu no caso do país Estados Unidos, onde foi identificada uma causalidade no sentido granger entre produção e preço em até 3 anos.
            Neste caso, pode-se dizer que a produção ajuda a explicar a evolução do preço no tempo;
            
            - Ao se comparar as previsões (dentro da amostra) realizadas entre o modelo _prophet_ e o _autogluon_,
            este apresenta melhor performance, segundo as métricas MAPE, MSE, MAE e MASE;
            
            - A sugestão é que, para fins de previsão para o preço de petroleo do tipo _brent_,
            o modelo _autogluon_ seja o mais adequado;
            
            - O modelo _prophet_ permite verificar como o erro se comporta ao longo do tempo, ou seja, quanto mais distante do
            último valor observado, mais o erro aumenta. O modelo _prophet_ tende a ser mais confiável em um horizonte de até 20 dias;
            
            - No horizonte de até 20 dias (fora da amostra) os resultados são os seguintes:
                - Preço de acordo com o modelo _autogluon_ em 01/07/2024:  US$ 80,35;
                - Preço de acordo com o modelo _prophet_ em 01/07/2024:  US$ 84,63;
                - Preço de fechamento observado em 01/07/2024:  US$ 86,60;
            
            - Apesar de durante o teste o modelo _autogluon_ ser mais confiável, o _prophet_ foi o que teve o melhor resultado (menores erros)
            quando comparado aos dados efetivamente observados. Apesar disso, o modelo _autogluon_ foi aquele que melhor conseguiu prever a trajetória da série,
            em que pese os valores previstos estarem relativamente mais distantes do observado quando se analisa as métricas de erro.
            
            - A recomendação é que o modelo _autogluon_ possa vir a ser o mais adequado, desde que melhor ajustado, pois acompanha melhor as alterações de tendência da série original. 
            </p>
            """, unsafe_allow_html=True)


# autogluon
# 	Performance
# MAPE	0.03
# RMSE	3.39
# MSE	11.49
# MAE	2.51
# RMSSE	1.18
# MASE	1.14
# SQL	1.73

# Prophet
# 	Performance
# MAPE	3.80
# RMSE	0.67
# MSE	15.76
# MAE	3.21
# MASE	7.26
# SMAPE	3.84
