"""
Código para recopilar información meteorológica de la página www.ogimet.com.

Guía para manejarse en la página:

    En la sección "Consulta de indicativos de estaciones meteorológicas de todo el mundo" 
    se puede obtener el indicativo correspondiente a la estación meteorológica deseada.
    Por ejemplo, para la ciudad de Córdoba, los indicativos son:
        87344 -> Córdoba Aerodrome
        87345 -> Córdoba Observatorio

    En la sección "Resúmenes diarios Ogimet" Se puede obtener un resumen diario en formato
    tabla para la estación meteorológica deseada, de acuerdo con su indicativo.

Este código realiza webscrapping para obtener los datos correspondientes a la tabla.
"""

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import time

## URL base donde se ubica la tabla que se desea scrappear
baseUrl = 'https://www.ogimet.com/cgi-bin/gsynres?ord=DIR&ndays=<day>&ano=<year>&mes=<month>&day=<day>&hora=18&ind=<ind>'

IND = 87344 ## Cordoba Aerodrome
year = 2017
month = 1
day= 31
months_to_download = 12
init_date = datetime.date(year, month, day)

def retrieve_data():
    """Obtiene los datos de la página y los almacena en un dataframe.

    Returns:
        df -- pandas.DataFrame con la información climática.
    """

    df = pd.DataFrame()

    ## Iteramos sobre meses porque en cada solicitud, obtenemos los datos
    ## correspondientes a un mes.
    for month in range(months_to_download):

        current_date = (init_date + relativedelta(months=month, day=31))
        replacedUrl = baseUrl \
            .replace('<day>', str(current_date.day)) \
            .replace('<month>', str(current_date.month)) \
            .replace('<year>', str(current_date.year)) \
            .replace('<ind>', str(IND))

        response = requests.get(replacedUrl)
        print(year, month, response)

        ## Repetimos el pedido hasta que no de error
        while response.status_code == 504:
            response = requests.get(replacedUrl)
            print('Retrying')

        ## Imprimimos la respuesta (200 significa respuesta exitosa)
        print(response)

        ## Este es todo el código html de la página
        soup = BeautifulSoup(response.text, 'html.parser')

        table = pd.read_html(str(soup.findAll('tr')[1]))
        table_data = table[1]

        ## Esta información no nos sirve
        del table_data['Diariometeorológico']

        table_data['Fecha'] = table_data['Fecha'] + '/' + str(current_date.year)

        df = df.append(table_data)
    return df

def parse_dataframe(df):
    """Parseamos el dataframe obtenido

    Arguments:
        df {pandas.DataFrame} -- Datos recopilados

    Returns:
        df -- Dataframe parseado
    """

    df.columns = df.columns.droplevel()
    to_rename = {
        'Max': 'Tmax',
        'Min': 'Tmin',
        'Med': 'Tmed'
    }
    df = df.rename(columns=to_rename)

    return df

df = retrieve_data()
df = parse_dataframe(df)
df.to_csv('../data/clima_dataset_{}.csv'.format(str(year)), index=False)