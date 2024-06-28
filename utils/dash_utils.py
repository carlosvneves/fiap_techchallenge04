import pandas as pd 
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np
import ipeadatapy as ip
from os.path import exists

# get data from ipea or reads from file
def get_ipea_data():
    if not exists('data/petr_brent.csv'):

        # baixa os dados do site do ipea
        #ip_metadata = ip.metadata()
        # busca do código da série de Preço - petróleo bruto - Brent (FOB)
        #ip_metadata[ip_metadata["NAME"].str.contains("Brent") == True]

        # seleção da série com dados a partir de 2001
        petr_brent = ip.timeseries("EIA366_PBRENT366", yearGreaterThan=2000)
        petr_brent.to_csv('data/petr_brent.csv')
    else:
        petr_brent = pd.read_csv('data/petr_brent.csv')

    return petr_brent


# load data and fill null values
def load_data():

    # get data from ipea or reads from file
    petr_brent = get_ipea_data()

    # print(petr_brent.head())
     
    # convert RAW DATE to datetime
    petr_brent['DATE'] = pd.to_datetime(petr_brent['DATE'])
      
    # select only DATE and VALUE (US$)
    petr_brent = petr_brent[['DATE','VALUE (US$)']]

    petr_brent.set_index('DATE', inplace=True )

    # select the first and last date
    start = petr_brent.index[0].date()
    end = petr_brent.index[len(petr_brent) - 1].date()
    new_dates = pd.date_range(start=start, end=end, freq="D")


    # reindex dates
    petr_brent = petr_brent.reindex(new_dates)

    # fill null values
    petr_brent["VALUE (US$)"] = petr_brent["VALUE (US$)"].interpolate().bfill()

    # rename columns
    petr_brent.columns = ['price']


    return petr_brent 

# calculate descriptive statistics
def descriptive_statistics(petr_brent):

    # calculate null values
    # null_sum = petr_brent['price'].isnull().sum()
    # not_null_sum = len(petr_brent) - null_sum
    #
    # print(null_sum, not_null_sum)
    #
    # # calculate descriptive statistics
    df_describe = pd.DataFrame({'price':petr_brent.describe()['price']}).reset_index()
    df_describe['index'] = ['Contagem', 'Média (US$)', 'Desvio Padrão (US$)', 'Mínimo (US$)', 'Quantil 25% (US$)', 'Mediana (US$)', 'Quantil 75% (US%)', 'Máximo (US$)']

    return df_describe

# load exogenous data
def load_exog_data():

    change_ener_consump = pd.read_csv("data/change-energy-consumption.csv")
    fossil_fuel_consump = pd.read_csv("data/fossil-fuel-consumption-by-type.csv")
    fossil_fuel = pd.read_csv("data/fossil-fuel-primary-energy.csv")
    oil_prod_country = pd.read_csv("data/oil-production-by-country.csv")
    oil_share = pd.read_csv("data/oil-share-energy.csv")
    energy_percapita = pd.read_csv("data/per-capita-energy-use.csv")

    return change_ener_consump, fossil_fuel_consump, fossil_fuel, oil_prod_country, oil_share, energy_percapita

def stationarity_test(series):
    series.dropna(inplace=True)
    result = adfuller(series)
    # print('ADF Statistic:', result[0])
    # print('p-value:', result[1])
    # for key, value in result[4].items():
    #     print('Critial Values:')
    #     print(f'   {key}, {value}')
    
    pvalue = result[1] 
    
    results = []
    
    if pvalue > 0.05:
        results.append(pvalue) 
        results.append("Não é estacionária.")
    else:
       results.append(pvalue)
       results.append("É estacionária.")
        
    return results  # return p-value

def granger_test(data):
    # x -> y

    x = data.iloc[:,0]
    y = data.iloc[:,1]


    x_stationary = stationarity_test(x)
    y_stationary = stationarity_test(y)

    # if x_stationary[0] > 0.05:
    #     x = np.diff(x)
    # if y_stationary[0] > 0.05:
    #     y = np.diff(y)
    # Ensure there are no missing values
    # x = x[~np.isnan(x)]  # x = x
    # y = y[~np.isnan(y)]

    if x_stationary[0] > 0.05 or y_stationary[0] > 0.05:
        x = np.diff(x)
        y = np.diff(y)
    else:
        x =  np.array(x)
        y =  np.array(y)
    
    data = pd.DataFrame({'x': x, 'y': y}, dtype=float).reset_index().drop(columns='index')

    # print(data.head())
    # Perform Granger causality test
    max_lag = 3
    granger_test_result = grangercausalitytests(data[["x","y"]], maxlag=max_lag, verbose=False)
    # Initialize the result list
    result = []

    # Interpret the results
    for lag in range(1, max_lag + 1):
        test_results = granger_test_result[lag][0]
        min_pvalue = min(test_results['ssr_ftest'][1], test_results['ssr_chi2test'][1], test_results['lrtest'][1], test_results['params_ftest'][1])
        if min_pvalue <= 0.05:
            causality_result = "granger causa"
        else:
            causality_result = "granger não-causa"
        
        result.append({lag: [min_pvalue, causality_result]})
    result.append({"estacionaridade": [x_stationary, y_stationary]})
     
    return result


def test_series(y, x, direction = 'y-x'):
    
    test_results = dict() 
    for country in x.columns[1:]:
        #st.write(country)
        # stationarity = stationarity_test(exogenous[country])
        try:
            xi = x[country]
            if direction == 'x-y':
                data = pd.merge(y,xi, on = 'Year')  
            elif direction == 'y-x':
                data = pd.merge(xi,y, on = 'Year')  
            res = granger_test(data)
        except Exception as e:
            res = e
        # st.write(res)
    
        test_results[country] = res
        # test_results[country].append(stationarity)
    return test_results

def extract_granger_result(cell):
    if isinstance(cell, dict):
        for value in cell.values():
            if len(value) > 1 and value[1] == 'granger causa':
                return value[1]
    return None



if __name__ == "__main__":

    petr_brent = load_data()

    print(petr_brent.describe())

    df_describe = descriptive_statistics(petr_brent)

    print(df_describe)
