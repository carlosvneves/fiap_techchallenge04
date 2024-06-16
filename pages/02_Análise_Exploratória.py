# carregamento de bibliotecas
# from os import truncate
import streamlit as st
import pandas as pd
import pytimetk as tk
# import numpy as np
# import matplotlib.pyplot as plt
import plotly.express as px
import utils.dash_utils as dash_utils
# import io
#from mitosheet.streamlit.v1 import spreadsheet

# TODO: use streamlit navigation bar: pip install streamlit-navigation-bar

# Begin
st.markdown(
    "<h1 style='text-align: center;'> Análise Exploratória </h1>",
    unsafe_allow_html=True
)

# load data
petr_brent = st.session_state.petr_brent

tab1, tab2, tab3 = st.tabs(["Série Temporal - Petróleo Brent", "Conhecendo melhor a série","Fatores Exógenos"])

with tab1:
    st.markdown("""

    # :chart: Dados Básicos
    """)


    # Using "with" notation
    #with st.sidebar:
    st.markdown("### Filtre por datas:")
    col01, col02 = st.columns(2)
    with col01:
        di = st.date_input("Data Inicial", petr_brent.index.min(), format = 'DD/MM/YYYY',
                           min_value=petr_brent.index.min(), max_value=petr_brent.index.max())
    with col02:
        df = st.date_input("Data Final", petr_brent.index.max(), format = 'DD/MM/YYYY',
                           min_value=petr_brent.index.min(), max_value=petr_brent.index.max())


    petr_brent_selected = petr_brent.loc[di:df]


    # calculate descriptive statistics
    df_describe = dash_utils.descriptive_statistics(petr_brent_selected)

    container = st.container(border=True)

    # Display descriptive statistics on screen
    # year of beginning and end
    # col01, col02 = st.columns(2)
    # col01.metric(label="Início da série", value = format(di, '%d/%m/%Y'))
    # col02.metric(label="Fim da série", value = format(df, '%d/%m/%Y'))


    row1 = container.columns(4)
    row2 = container.columns(4)


    i = 0
    for col in row1 + row2:
        col.metric(label= df_describe.loc[i, 'index'], value = format(df_describe.loc[i, 'price'], '.2f'))
        i += 1


    container = st.container(border=True)

    # Original time series chart
    fig = px.line(
        petr_brent_selected.reset_index(),
        x="index",
        y="price",
    )

    fig.update_layout(
        title="Preços do petroleo Brent",
        xaxis_title="Data",
        yaxis_title="Preço (US$)",
    )



    with container:
        st.markdown("""
        ### Preço do Petróleo do tipo Brent em US$

        <p style="text-align: justify">A série de preços históricos do petróleo do tipo <b>brent</b> foi obtida da base do Ipea, por meio de uma API Python:
        <a href="https://github.com/luanborelli/ipeadatapy">[`ipeadatapy`]</a>. A API permite que os usuários obtenham dados a partir do
        código da série temporal. No caso do petróleo do tipo <b>brent</b>, a série é a de código <b>EIA366_PBRENT366</b>, que é de
        periodicidade diária, e com início em 2001.
        A série foi ajustada para não conter valores nulos por meio dos métodos <i>interpolate()</i> e <i>bfill()</i> da biblioteca <i>pandas</i>.

        </p>

        """, unsafe_allow_html=True
    )

    container.plotly_chart(fig)

with tab2:


    # Seasonal Decomposition
    container = st.container(border=True)

    container.write("""
        ### Decomposição da série em suas componentes de tendência, sazonalidade e erro.

        <p style="text-align: justify">
        A decomposição permite verificar qual o tipo de processo gerador da séries temporal e, consequentemente, qual o
        tipo de modelo pode ser mais adequado para compreender a série e realizar previsões.
        No caso, a série não é estacionária, logo, <b>deverá ser realizado um trabalho de tratamento da série
        para facilitar a construção de um modelo preditivo</b>.
        </p>


    """, unsafe_allow_html=True)

    anomalize_df = tk.anomalize(
        data          = petr_brent.reset_index(),
        date_column   = 'index',
        value_column  = 'price',
        period        = 7,
        iqr_alpha     = 0.05, # using the default
        clean_alpha   = 0.75, # using the default
        clean         = "min_max"
    )

    anomalize_df.rename(columns={'index': 'date'}, inplace=True)

    # st.write(anomalize_df)

    # Plot seasonal decomposition
    container.plotly_chart(
        tk.plot_anomalies_decomp(
        data        = anomalize_df,
        date_column = 'date',
        engine      = 'plotly',
        title       = 'Seasonal Decomposition'
    )
    )


    # Anomalies detection
    container = st.container(border=True)

    with container:
        st.markdown(f"""
        ### Detecção de Anomalias

        <p style="text-align: justify">
        A detecção de anomalias permite verificar se existem anomalias nos dados de preços do petróleo do tipo Brent. São identificados diversos valores que podem ser considerados atípicos, os quais estãp marcados em vermelho.
        Os dados anômalos podem então ser tratados e a série estará pronta para se para construir modelos preditivos.
        </p>

        """, unsafe_allow_html=True
    )


    # Plot anomalies
    container.plotly_chart(
        tk.plot_anomalies(
        data        = anomalize_df,
        date_column = 'date',
        engine      = 'plotly',
        title       = 'Anomalias Detectadas'
    )
    )

    # Plot cleaned anomalies
    container.plotly_chart(
        tk.plot_anomalies_cleaned(
        data        = anomalize_df,
        date_column = 'date',
        engine      = 'plotly',
        title       = 'Série após o Processo de "limpeza" de anomalias'
    )
    )

with tab3:
    st.markdown(f"""
        ### Fatores Exógenos

        <p style="text-align: justify">
        <b>Quais fatores podem influenciar o comportamento do preço do petróleo?</b>

        </p>


    """, unsafe_allow_html= True)
    # reads data from file
    change_ener_consump, fossil_fuel_consump, fossil_fuel, oil_prod_country, oil_share, energy_percapita  = dash_utils.load_exog_data()


    supply_tab, demand_tab, exog_tab = st.tabs(["Produção de petróleo", "Consumo de petróleo","Choques externos e impactos no preço do petróleo"])

    st.divider()

    with supply_tab:

        st.markdown(f"""
            #### Produção de petróleo no mundo


            <p style="text-align: justify">
               <b>Quanto de petróleo é produzido no mundo? Quais países mais produzem petróleo?</b>

               No mapa interativo é possível ver a produção de petróleo de cada país por ano. A produção foi convertida em terawatt-hora de energia para permitir a melhor comparação.
               </p>

        """, unsafe_allow_html=True)

        oil_prod_country_gt_2001 = oil_prod_country.query("Year > 2001")
        oil_prod_country_gt_2001['Code'] = oil_prod_country_gt_2001['Code'].astype(str)
        oil_prod_country_gt_2001 = oil_prod_country_gt_2001.query("Code != 'nan' and Entity != 'World'")


        min_value = oil_prod_country_gt_2001["Oil production (TWh)"].min()
        max_value = oil_prod_country_gt_2001["Oil production (TWh)"].max()

        fig = px.choropleth(
            oil_prod_country_gt_2001,
            locations="Code",
            color="Oil production (TWh)",  # lifeExp is a column of gapminder
            hover_name="Entity",  # column to add to hover information
            animation_frame="Year",
            range_color=(min_value, max_value),
            color_continuous_scale= "Viridis",#px.colors.sequential.Plasma,
        )
        # Update the layout to set the figure size
        fig.update_layout(
            width=800,
            height=600,  # Adjust the width as needed  # Adjust the height as needed
        )
        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            coloraxis_colorbar=dict(
                orientation="h",  # Define orientação horizontal
                yanchor="bottom",
                xanchor="center",
                x=0.5,
                y=-0.2,
            ),
        )

        st.plotly_chart(fig)

        st.divider()

        st.markdown(f"""
            #### Produção de petróleo no tempo


            <p style="text-align: justify">
                <b>Como tem evoluído a produção de petróleo no mundo ao longo desde 2002? </b>

            O gráfico interativo permite ver a tendência de aumento na produção de petróleo dos principais países produtores desde 2002.
            </p>

        """, unsafe_allow_html=True)

        oil_prod_country_gt_2001 = oil_prod_country_gt_2001.query("Entity in ('United States','Saudi Arabia' ,'Iraq', 'United Arab Emirates', 'Norway', 'Oman', \
        'Qatar', 'Russia')")
        fig = px.line(
            oil_prod_country_gt_2001,
            x="Year",
            y="Oil production (TWh)",
            color="Entity",
        )
        # Update the layout to set the figure size
        fig.update_layout(
            width=800, height=600  # Adjust the width as needed  # Adjust the height as needed
        )
        st.plotly_chart(fig)






    with demand_tab:

        st.markdown(f"""
            #### Consumo de combustível Fossil (TWh)


            <p style="text-align: justifVy">
            <b>Quais fatores podem influenciar o comportamento do preço do petróleo? Qual é a relação entre os fatores exógenos e as anomalias identificadas?</b>
            </p>

        """, unsafe_allow_html=True)


        fossil_fuel_gt_2001 = fossil_fuel.query("Year > 2001")

        fossil_fuel_gt_2001['Code'] = fossil_fuel_gt_2001['Code'].astype(str)
        fossil_fuel_gt_2001 = fossil_fuel_gt_2001.query("Code != 'nan' and Entity != 'World'")

        min_value = fossil_fuel_gt_2001["Fossil fuels (TWh)"].min()
        max_value = fossil_fuel_gt_2001["Fossil fuels (TWh)"].max()

        fig = px.choropleth(
            fossil_fuel_gt_2001,
            locations="Code",
            color="Fossil fuels (TWh)",  # lifeExp is a column of gapminder
            hover_name="Entity",  # column to add to hover information
            animation_frame="Year",
            range_color=(min_value, max_value),
            color_continuous_scale="Viridis",
        )
        # Update the layout to set the figure size
        fig.update_layout(
            width=800,
            height=600,  # Adjust the width as needed  # Adjust the height as needed
        )
        fig.update_layout(
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            coloraxis_colorbar=dict(
                orientation="h",  # Define orientação horizontal
                yanchor="bottom",
                xanchor="center",
                x=0.5,
                y=-0.2,
            ),
        )

        st.plotly_chart(fig)

        st.divider()

        st.markdown(f"""
            #### Variação anual no Consumo de Energia (%)


            <p style="text-align: justifVy">
            <b>Quais fatores podem influenciar o comportamento do preço do petróleo? Qual é a relação entre os fatores exógenos e as anomalias identificadas?</b>

            Para agregados representativos.
            </p>

        """, unsafe_allow_html=True)

        # change_ener_consump_gt_2001 = change_ener_consump.query(
        #     "Entity in ('OECD (EIA)', 'Lower-middle-income countries', 'Asia & Oceania (EIA)', 'Australia and New Zealand (EIA)', \
        #         'Europe (EIA)', 'Upper-middle-income countries', 'High-income countries','South and Central America (EI)') \
        #             and Year > 2001"
        # )


        change_ener_consump_gt_2001 = change_ener_consump.query("Year > 2001")



        # limits the displayed country names by value
        change_ener_consump_gt_2001['Code'] = change_ener_consump_gt_2001['Code'].astype(str)
        change_ener_consump_gt_2001['Entity'] = change_ener_consump_gt_2001['Entity'].astype(str)
        change_ener_consump_gt_2001 = change_ener_consump_gt_2001.query("Entity in ('United States','Brazil' ,'China', 'Japan', 'Germany', 'United Kingdom', \
            'Canada', 'India', 'France', 'Norway','South Africa') ")
        # change_ener_consump_gt_2001 = change_ener_consump_gt_2001.query("Code == 'nan' and `Annual change in primary energy consumption (%)` > -10")


        fig = px.line(
            change_ener_consump_gt_2001,
            x="Year",
            y="Annual change in primary energy consumption (%)",
            color="Entity",
        )
        # Update the layout to set the figure size
        fig.update_layout(
            width=800, height=600  # Adjust the width as needed  # Adjust the height as needed
        )

        st.plotly_chart(fig)
with exog_tab:

    st.markdown(f"""
        #### Fatores Exógenos

        <p style="text-align: justify">
        <b>Quais fatores podem influenciar o comportamento do preço do petróleo?</b>

        </p>


    """, unsafe_allow_html= True)

    # from daily to annual
    price = anomalize_df[["date","observed_clean"]]
    price.rename(columns={"observed_clean":"price"}, inplace=True)
    price_y = price.set_index('date').resample("Y").mean()

    # price percent change
    price_y_percent_change = price_y.resample("Y").sum().pct_change() * 100

    # oil production data frame
    df_production = oil_prod_country_gt_2001.reset_index()[
        ["Entity", "Year", "Oil production (TWh)"]
    ].pivot(index="Year", columns="Entity", values="Oil production (TWh)")

    # price data frame
    df_price = price_y.reset_index()
    df_price["Year"] = df_price["date"].dt.year
    df_price = df_price.drop(columns="date", axis=1)
    df_price.set_index("Year", inplace=True)

    # normalize data
    from sklearn.preprocessing import MinMaxScaler
    import plotly.graph_objs as go

    # Normalizing the production data
    scaler = MinMaxScaler()
    normalized_production = df_production.copy()
    normalized_production.iloc[:, 1:] = scaler.fit_transform(
        df_production.iloc[:, 1:].to_numpy()
    )

    # Normalizing the price data
    normalized_price = df_price.copy().reset_index()
    normalized_price.iloc[:, 1:] = scaler.fit_transform(normalized_price.iloc[:, 1:])
    normalized_price.set_index("Year", inplace=True)

    # Create traces for each country's production values
    traces = []
    for country in normalized_production.columns[1:]:  # Exclude the 'Year' column
        trace = go.Scatter(
            x=normalized_production.index,
            y=normalized_production[country],
            mode="lines",
            name=f"{country} Produção",
            line=dict(dash="solid"),  # Solid lines for production values
            opacity=0.45,
        )
        traces.append(trace)

    # Create a trace for the yearly price series, using a secondary y-axis
    trace_price = go.Scatter(
        x=normalized_price.index,
        y=normalized_price["price"],
        mode="lines+markers",
        name="Preço",
        yaxis="y2",
        line=dict(dash="dot", color="red"),  # Dotted line and red color for price values
    )
    traces.append(trace_price)

    # Create the layout
    layout = go.Layout(
        title="Produção e Preço anual do Petroleo normalizados",
        xaxis=dict(title="Ano"),
        yaxis=dict(title="Produção normalizada"),
        yaxis2=dict(title="Preço normalizado", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="right", x=1),
        height= 600,
        width= 800,
    )

    # Combine the traces into a figure
    fig = go.Figure(data=traces, layout=layout)

    # Show the plot
    st.plotly_chart(fig)

    # fig = px.line(
    #     price_y_percent_change,
    #     title="Variação anual do preço do Petróleo do tipo Brent (%)",
    #     labels={"index": "Ano", "value": "Variação (%)"},
    # )

    # st.plotly_chart(fig)

    # consumption percent change
    df_consump_pct_change = change_ener_consump_gt_2001[['Year', 'Entity','Annual change in primary energy consumption (%)']].copy()
    df_consump_pct_change.rename(columns={'Annual change in primary energy consumption (%)': 'Percent Change', "Entity": "Type"}, inplace=True)
    df_consump_pct_change.set_index('Year', inplace=True)

    # st.write(df_consump_pct_change.head())
    
    # df_consump_melted = df_consump_pct_change.reset_index().melt(
    #     id_vars=["Year"], var_name="Type",  
    #     value_vars= ["Entity", "Percent Change"], 
        
    # )

    # st.write(df_consump_melted)

    # price percent change
    price_y_percent_change = price_y.resample("Y").sum().pct_change() * 100

    # price data frame
    df_price_pct_change = price_y_percent_change.reset_index()

    df_price_pct_change["Year"] = df_price_pct_change["date"].dt.year
    df_price_pct_change = df_price_pct_change.drop(columns="date", axis=1)

    # prepare the price data frame to concatenate
    df_price_melted = df_price_pct_change.reset_index().melt(
        id_vars=["Year"], var_name="Type", value_vars = "price", value_name="Percent Change",
    )
    df_price_melted.set_index('Year', inplace=True)

    # st.write(df_price_melted)

    # Combine the concumption and price data for plotting
    # df_combined = pd.concat([df_consump_pct_change, df_price_melted])
    #df_combined["Type"] = df_combined["Type"].fillna(df_combined["Entity"])
    # df_combined.drop(columns=["Entity"], inplace=True)
    # df_combined.reset_index(inplace=True)
    # Plot the data
    # fig = px.line(df_combined, x="Year", y="Percent Change", color="Type")
    # st.plotly_chart(fig)
    st.divider()
    
    df_consump_pct_change.reset_index(inplace=True)
    #transform from long to wide format
    df_consump_pct_change = df_consump_pct_change.pivot(index="Year", columns="Type", values="Percent Change")

    # Create traces for each country's production values
    traces = []
    for country in df_consump_pct_change.columns[1:]:  # Exclude the 'Year' column
        trace = go.Scatter(
            x=df_consump_pct_change.index,
            y=df_consump_pct_change[country],
            mode="lines",
            name=f"{country} Consumo",
            line=dict(dash="solid"),  # Solid lines for production values
            opacity=0.45,
        )
        traces.append(trace)

    # Create a trace for the yearly price series, using a secondary y-axis
    trace_price = go.Scatter(
        x=df_price_pct_change["Year"],
        y=df_price_pct_change["price"],
        mode="lines+markers",
        name="Preço",
        yaxis="y2",
        line=dict(dash="dot", color="red"),  # Dotted line and red color for price values
    )
    traces.append(trace_price)

    # Create the layout
    layout = go.Layout(
        title="Variação anual do Consumo de Energia e de Preços do Petróleo do tipo Brent (%)",
        xaxis=dict(title="Ano"),
        yaxis=dict(title="Consumo de energia (%)"),
        yaxis2=dict(title="Variação de preços (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="right", x=1),
        height= 600,
        width= 800,
    )

    # Combine the traces into a figure
    fig = go.Figure(data=traces, layout=layout)

    st.plotly_chart(fig)

    
    # stationationarity test
    # res = dash_utils.stationarity_test(df_price['price'])
    # st.write(res)

    # res = dash_utils.stationarity_test(df_price_pct_change['price'])
    # st.write(res)

    # granger test - preço granger-causa consumo
    df_price_pct_change = df_price_pct_change[['Year', 'price']].set_index('Year')
    # granger_result = dict() 
    # for country in df_consump_pct_change.columns[1:]:
    #     # st.write(country)
    #     # st.write(dash_utils.stationarity_test(df_consump_pct_change[country]))
    #     try:
    #         y = df_consump_pct_change[country]
    #         data = pd.merge(x,y, on = 'Year')  
    #         # st.write(data)
    #         res = dash_utils.granger_test(data)
    #     except Exception as e:
    #         res = e
    #     # st.write(res)
    #     granger_result[country] = res
    
    # st.write(x)
    # st.write(y)
    
    st.write('## Teste de Granger - Produção -> Preço')
    granger_result_prod = dash_utils.test_series(y=normalized_price, x=normalized_production, direction = 'x-y') 
    st.write(pd.DataFrame(granger_result_prod))

    st.write('## Teste de Granger - Preço -> Produção')
    granger_result_prod = dash_utils.test_series(y=normalized_price, x=normalized_production, direction = 'y-x') 
    st.write(pd.DataFrame(granger_result_prod))
    
    st.write('## Teste de Granger - Consumo -> Preço')
    granger_result_cons = dash_utils.test_series(y=df_price_pct_change, x=df_consump_pct_change, direction = 'x-y') 
    st.write(pd.DataFrame(granger_result_cons))

    # granger test - produção granger-causa preço
    # y = normalized_price
    # granger_result_prod = dict() 
    # for country in normalized_production.columns[1:]:
    #     st.write(country)
    #     st.write(dash_utils.stationarity_test(normalized_production[country]))
    #     try:
    #         y = normalized_production[country]
    #         data = pd.merge(x,y, on = 'Year')  
    #         # st.write(data)
    #         res = dash_utils.granger_test(data)
    #     except Exception as e:
    #         res = e
    #     # st.write(res)
    #     granger_result_prod[country] = res
    
    # st.write(x)
    # st.write(y)


