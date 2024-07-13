# Alura+Pós-Tech - TechChallenge 04 #

#### __Repositório__: https://github.com/carlosvneves/fiap_techchallenge04 

#### __Aplicação__ : https://fiaptechchallenge04-3dtat.app/


#### Desenvolvido por: *Carlos Eduardo Veras Neves* - rm 353068


## Descrição do Problema

---
<div><p>
          Você foi contratado(a) para uma consultoria, e seu trabalho envolve analisar os dados de preço do petróleo brent, que pode ser encontrado no <a href="http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&amp;serid=1650971490&amp;oper=view" target="_blank">site do ipea</a>. Essa base de dados histórica envolve duas colunas: data e preço (em dólares). 
        </p>
        <p>
          Um grande cliente do segmento pediu para que a consultoria desenvolvesse um dashboard interativo e que gere insights relevantes para tomada de decisão. Além disso, solicitaram que fosse desenvolvido um modelo de Machine Learning para fazer o forecasting do preço do petróleo.
        </p>
        <p>
          <span>Seu objetivo é</span>:
        </p></div>
<div><ul>
          <li>
            <p>
              Criar um dashboard interativo com ferramentas à sua escolha.
            </p>
          </li>
          <li>
            <p>
              Seu dashboard deve fazer parte de um storytelling que traga insights relevantes sobre a variação do preço do petróleo, como situações geopolíticas, crises econômicas, demanda global por energia e etc. Isso pode te ajudar com seu modelo. É obrigatório que você traga pelo menos 4 insights neste desafio.
            </p>
          </li>
          <li>
            <p>
              Criar um modelo de Machine Learning que faça a previsão do preço do petróleo diariamente (lembre-se de time series). Esse modelo deve estar contemplado em seu storytelling e deve conter o código que você trabalhou, analisando as performances do modelo.
            </p>
          </li>
          <li>
            <p>
              Criar um plano para fazer o deploy em produção do modelo, com as ferramentas que são necessárias.
            </p>
          </li>
          <li>
            <p>
              Faça um MVP do seu modelo em produção utilizando o Streamlit.
            </p>
          </li>
        
</ul></div>

---

## Base de Dados

#### Série Temporal do Preço do Petróleo do tipo Brent no [ipea-data](http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view)

---
## Metodologia

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


## Modelos para previsão de séries temporais

### [Prophet](https://facebook.github.io/prophet/) 
  
### [Autogluon](https://auto.gluon.ai/stable/index.html)