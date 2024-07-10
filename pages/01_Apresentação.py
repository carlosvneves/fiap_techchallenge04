import streamlit as st

import streamlit.components.v1 as components

st.set_page_config(page_title="Pipeline de Machine Learning", layout="wide")

def mermaid(code: str) -> None:
    components.html(
        f"""
        <div class="mermaid">
            {code}
        </div>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """
    )

st.header("Sobre o problema de negócio 📊")
st.markdown("""
            ---
            ### Descrição do problema:
            

            Você foi contratado(a) para uma consultoria, e seu trabalho envolve analisar os dados de preço do petróleo brent, que pode ser encontrado no site do ipea. Essa base de dados histórica envolve duas colunas: data e preço (em dólares).

            Um grande cliente do segmento pediu para que a consultoria desenvolvesse um dashboard interativo e que gere insights relevantes para tomada de decisão. Além disso, solicitaram que fosse desenvolvido um modelo de Machine Learning para fazer o forecasting do preço do petróleo.

            ---
            ### Objetivo:

            - Criar um dashboard interativo com ferramentas à sua escolha.
            - Seu dashboard deve fazer parte de um storytelling que traga insights relevantes sobre a variação do preço do petróleo, como situações geopolíticas, crises econômicas, demanda global por energia e etc. Isso pode te ajudar com seu modelo. É obrigatório que você traga pelo menos 4 insights neste desafio.
            - Criar um modelo de Machine Learning que faça a previsão do preço do petróleo diariamente (lembre-se de time series). Esse modelo deve estar contemplado em seu storytelling e deve conter o código que você trabalhou, analisando as performances do modelo.
            - Criar um plano para fazer o deploy em produção do modelo, com as ferramentas que são necessárias.
            - Faça um MVP do seu modelo em produção utilizando o Streamlit.

            ---
            ### Descrição da solução:

            O problema de negócio será solucionado por meio de um _pipeline_ de _Machine Learning_ implementado em Python/Streamlit. A seguir se tem as etapas para construção do pipeline de _Machine Learning_ e alguns exemplos de tarefas relacionadas.
""")

mermaid(
    """
        graph LR
            A[Entendimento do Problema de Negócio] --> B[Tratamento dos Dados]
            B --> C[Análise Exploratória dos Dados]
            C --> D[Construção do Modelo Preditivo]
            D --> E[Avaliação do Modelo Preditivo]
            E --> F[Deploy]

            style A fill:#f9f,stroke:#333,stroke-width:2px
            style B fill:#9f9,stroke:#333,stroke-width:2px
            style C fill:#9ff,stroke:#333,stroke-width:2px
            style D fill:#ff9,stroke:#333,stroke-width:2px
            style E fill:#f99,stroke:#333,stroke-width:2px
            style F fill:#99f,stroke:#333,stroke-width:2px
    """
)
st.markdown("""
            ### 1. Entendimento do Problema de Negócio
            - Analisar e definir claramente o problema que o modelo de machine learning deve resolver.
            - Identificar os objetivos de negócio e os requisitos do projeto.

            ### 2. Tratamento dos Dados
            - Coleta dos dados brutos.
            - Limpeza dos dados para remover ou corrigir valores faltantes e inconsistentes.
            - Transformação dos dados para o formato adequado para análise.

            ### 3. Análise Exploratória dos Dados
            - Analisar estatísticas descritivas dos dados.
            - Visualizar distribuições e relações entre variáveis.
            - Identificar padrões, tendências e outliers.

            ### 4. Construção do Modelo Preditivo
            - Seleção e aplicação de algoritmos de machine learning.
            - Treinamento do modelo com os dados disponíveis.
            - Ajuste de hiperparâmetros para otimização do modelo.

            ### 5. Avaliação do Modelo Preditivo
            - Testar o modelo com um conjunto de dados separado (validação).
            - Calcular métricas de desempenho, como acurácia, precisão, recall, F1-score, etc.
            - Comparar diferentes modelos para selecionar o melhor.

            ### 6. Deploy
            - Implementação do modelo selecionado em um ambiente de produção.
            - Monitoramento do desempenho do modelo em tempo real.
            - Atualizações e reentrenamento do modelo conforme necessário.
            """)
