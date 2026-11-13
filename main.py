import pandas as pd 
import numpy as np 
from sklearn.linear_model import LinearRegression 

pd.set_option('display.max_rows', None) 
pd.set_option('display.max_columns', None) 
pd.set_option('display.width', None)

def leer_csv(path:str)->pd.DataFrame:
    """Leer datasets"""
    return pd.read_csv(path)

def convertir_fecha_datetime(data:pd.DataFrame)->pd.DataFrame: 
    df_estacion=data 
    # 1. Intentar el formato ISO estándar (YYYY-MM-DD)
    fecha_iso=pd.to_datetime(df_estacion["fecha"], format="%Y-%m-%d", errors="coerce")
    # 2. Para los valores que no cumplieron el formato ISO (producen NaT) aplicar el formato local dayfirst=True
    fecha_nat=fecha_iso.isna()
    if fecha_nat.any(): 
            fecha_locales=pd.to_datetime(
                df_estacion.loc[fecha_nat, "fecha"], 
                dayfirst=True, 
                errors="coerce"
            )
            fecha_iso.fillna(fecha_locales, inplace=True)
    df_estacion["fecha"]=fecha_iso
    
    return df_estacion

def obtenerPrecipitacion(data: pd.DataFrame)->pd.DataFrame:

     precipitacion=data 
     return precipitacion

def imputar_precipitacion(data:pd.DataFrame)->pd.DataFrame: 
     """
    Limpia los valores negativos de precipitación, entrena un modelo de regresión lineal
    con los datos válidos y realiza la imputación condicional basada en humedad >= 70%.
    """

     
     df_estacion=data 

     # 1. Saneamiento inicial: Forzar a NaN los valores negativos de precipitación
     precipitaciones_invalidas=df_estacion["precipitacion_mm"]<0
     df_estacion.loc[precipitaciones_invalidas, "precipitacion_mm"]=np.nan 

     # 2. Definir variables predictoras y objetivo usando únicamente datos limpios y completos
     features=["temp_max_c", "temp_min_c", "humedad_pct", "viento_kmh"]

     datos_validos=(
          (df_estacion["precipitacion_mm"].notna()) & 
          (df_estacion[features].notna().all(axis=1)) & 
          (df_estacion["precipitacion_mm"]>=0)
     )

     # 3. Entrenar el modelo de Regresión Lineal
     X_train=df_estacion.loc[datos_validos, features]
     Y_train=df_estacion.loc[datos_validos, "precipitacion_mm"]

     modelo=LinearRegression() 
     models=modelo.fit(X=X_train, y=Y_train)

     # 4. Definir la máscara para las filas que requieren imputación:
    # - Precipitación es NaN (por el saneamiento previo de negativos o faltantes originales)
    # - Humedad relativa es del 70% o más (>= 70.0)
     datos_imputar=(
          (df_estacion["precipitacion_mm"].isna()) & 
          (df_estacion["humedad_pct"]>=70) & 
          (df_estacion[features].notna().all(axis=1))
     )

     # 5. Predecir e imputar solo en esas filas específicas
     if datos_imputar.any(): 
          X_imputar=df_estacion.loc[datos_imputar, features]
          predicciones=models.predict(X_imputar) 

          # Nos aseguramos de que no devuelva valores negativos por desvíos del modelo
          predicciones=np.clip(predicciones, a_min=0.0, a_max=None)
          df_estacion.loc[datos_imputar, "precipitacion_mm"]=predicciones

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



df_estacion["viento_kmh_interpolacion"]=(
    df_estacion.set_index("fecha")["viento_kmh"]
    .interpolate(method='time', limit=3, limit_area='inside') 
    .values 
) ## Realiza la interpolacion de la variable viento


df_estacion.drop(["temp_max_c", "temp_min_c", "humedad_pct",  "viento_kmh"], axis=1, inplace=True) #Se elimina las variables que no se utilizan

df_estacion.rename(columns={ 
    "temp_max_interpolacion":"temp_max_c", 
    "temp_min_c_decimal":"temp_min_c", 
    "humedad_pct_interpolacion":"humedad_pct", 
    "precipitacion_mm_interpolacion":"precipitacion_mm", 
    "viento_kmh_interpolacion":"viento_kmh"
}, inplace=True) #Se renombra las columnas 

df_estacion["estado_sensor"]=df_estacion["estado_sensor"].str.strip().str.lower() ##Se convierte la columna del estado del sensor a minuscula


sensor_no_operativo=df_estacion["estado_sensor"].isin(["falla", "mantenimiento"])

precipitaciones_invalidas=df_estacion["precipitacion_mm"].isna() | (df_estacion["precipitacion_mm"]<0) 

df_estacion.loc[sensor_no_operativo & precipitaciones_invalidas, "precipitacion_mm"]=0

humedad_ubral_70=df_estacion["humedad_pct"]<70 
df_estacion.loc[precipitaciones_invalidas & humedad_ubral_70, "precipitacion_mm"]=0

df_estacion=imputar_precipitacion(data=df_estacion)
print(df_estacion)
