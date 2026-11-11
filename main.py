import pandas as pd 
import numpy as np 

pd.set_option('display.max_rows', None) 
pd.set_option('display.max_columns', None) 
pd.set_option('display.width', None)

def leer_csv(path:str)->pd.DataFrame:
    """Leer datasets"""
    return pd.read_csv(path)

def convertir_fecha_datetime(data:pd.DataFrame)->pd.DataFrame: 
    """Convertir la columna fecha a un formato datetime uniforme"""
    df_estacion=data 
    df_estacion["fecha"]=pd.to_datetime(data["fecha"], format="mixed", dayfirst=True)
    return df_estacion

path='estacion_meteorologica_2025.csv'
estacion=leer_csv(path=path)
"""Tipo de datos de las variables de análisis"""
print(estacion.dtypes)



"""Análisis de medida estadistica"""
print(estacion.describe())

df_estacion=convertir_fecha_datetime(estacion)
"""Elimina duplicado y ordena el dataset de menor a mayor"""
df_estacion=df_estacion.drop_duplicates().sort_values("fecha").reset_index(drop=True)
df_estacion["temp_max_interpolacion"]=df_estacion["temp_max_c"].replace(-999.0, np.nan)

df_estacion["temp_max_interpolacion"]=(
                    df_estacion.set_index("fecha")["temp_max_interpolacion"]
                    .interpolate(method="time",limit=3, limit_area='inside') 
                    .values
) ##Realiza la interpolacion de la variable de temperatura maxima 

"""Se reemplaza la coma por el punto decimal en la variable de temperatura minima"""
df_estacion["temp_min_c_decimal"]=(
                df_estacion["temp_min_c"]
                .astype(str) 
                .str.strip() 
                .replace(',','.', regex=True)   
)

df_estacion["temp_min_c_decimal"]=pd.to_numeric(df_estacion["temp_min_c_decimal"]) #Se convierte la columna de temperatura minima a tipo de datos flotante

df_estacion["temp_min_c_decimal"]=(
    df_estacion.set_index("fecha")["temp_min_c_decimal"]
    .interpolate(method="time", limit=3, limit_area="inside")
    .values
) ## Realiza la interpolacion de la variable de tempertura minima 


df_estacion["humedad_pct_interpolacion"]=df_estacion["humedad_pct"].replace(-999, np.nan) 

df_estacion["humedad_pct_interpolacion"]=(
    df_estacion.set_index("fecha")["humedad_pct_interpolacion"]
    .interpolate(method='time', limit=3, limit_area='inside')
    .values 
) ## Realiza la interpolacion de la variable humedad

df_estacion["precipitacion_mm_interpolacion"]=df_estacion['precipitacion_mm'].where(df_estacion["precipitacion_mm"]>=0)

df_estacion["precipitacion_mm_interpolacion"]=(
    df_estacion.set_index("fecha")["precipitacion_mm_interpolacion"]
    .interpolate(method="time", limit=3, limit_area='inside')
    .values
) ## Realiza la interpolación de la variable precipitacion

df_estacion["viento_kmh_interpolacion"]=(
    df_estacion.set_index("fecha")["viento_kmh"]
    .interpolate(method='time', limit=3, limit_area='inside') 
    .values 
) ## Realiza la interpolacion de la variable viento

df_estacion["estado_sensor"]=df_estacion["estado_sensor"].str.strip().str.lower() ##Se convierte la columna del estado del sensor a minuscula

df_estacion.drop(["temp_max_c", "temp_min_c", "humedad_pct", "precipitacion_mm", "viento_kmh"], axis=1, inplace=True) #Se elimina las variables que no se utilizan

df_estacion.rename(columns={ 
    "temp_max_interpolacion":"temp_max_c", 
    "temp_min_c_decimal":"temp_min_c", 
    "humedad_pct_interpolacion":"humedad_pct", 
    "precipitacion_mm_interpolacion":"precipitacion_mm", 
    "viento_kmh_interpolacion":"viento_kmh"
}, inplace=True) #Se renombra las columnas 

print(df_estacion)