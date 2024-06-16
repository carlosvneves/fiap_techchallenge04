import pandas as pd 
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
        petr_brent = ip.timeseries("EIA366_PBRENT366", yearGreaterThan=2001)
        petr_brent.to_csv('data/petr_brent.csv')
    else:
        petr_brent = pd.read_csv('data/petr_brent.csv')

    return petr_brent


# load data and fill null values
def load_data():

    # get data from ipea or reads from file
    petr_brent = get_ipea_data()
     
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


    pass
if __name__ == "__main__":

    petr_brent = load_data()

    print(petr_brent.describe())

    df_describe = descriptive_statistics(petr_brent)

    print(df_describe)

