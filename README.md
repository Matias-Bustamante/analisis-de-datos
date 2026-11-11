
## Tipo de datos 

### Fecha: String
### temp_max_c: float64 
### temp_min: string 
### humedad_pct: int64 
### precipitacion_mm: float64 
### viento_kmh: float64 
### estado_sensor: string 
### estacion: string 

## Anomalias 
1) La columna fecha se encuentra escrito en diferente formato. 
2) En la temperatura minima se utiliza eiferentes simbolos para separar el punto decimal.
3) La columna precipitacion_mm contiene valores de NAN (No es un número). 
4) La columna estado sensor es una variable de tipo cualitativa con valores en mayuscula, minuscula y espacio en blanco. 

## Análisis estadistico de medida de posición y dispersión
1) temp_max_c
    1. Total registro: 371 
    2. Media aritmetica: 2.17 (centigrado). 
    3. Desvio estandar: 149.22 (centigrado). 
    4. Minimo: -999 (centigrado)
    5. Q1 (25%): 16.65
    6. Q2 (50%): 22.70 
    7. Q3 (75%): 29.00
    8. Máximo: 96.60 (centigrado). 
2. humedad_pct
    1. Total registro: 371 
    2. Media aritmetica: 44.58 (pct). 
    3. Desvio estandar: 123.30 (pct). 
    4. Mínimo: -999 (pct). 
    5. Q1 (25%): 48
    6. Q2 (50%): 58 
    7. Q3 (75%): 68 
    8. Máximo: 160 (pct). 
3. precipitacion_mm
    1. Total registro: 364 (371-364)=7 registros nulos.
    2. Media aritmetica: 3.14 (mm). 
    3. Desvio estandar: 9.96 (mm). 
    4. Minimo:-4.40 (mm). 
    5. Q1 (25%): 0 
    6. Q2 (50%): 0 
    7. Q3 (75%): 0 
    7. Máximo: 80.5 (mm). 
4. viento_kmh
    1. Total registro: 370 (371-370)=1 registro nulos. 
    2. Media aritmetica: 13.26 (km/h). 
    3. Desvio estandar: 6.29 (km/h). 
    4. Mínimo: 0.10 (km/h). 
    5. P1 (25%): 8.82
    6. P2 (50%): 13.05
    7. P3 (75%): 17.97 
    8. Máximo: 34 (km/h)

# Tratamientos de valores faltantes e inválidos 
Los valores faltantes y valores fisicamente imposibles, como precipitaciones negativas se reemplazaron con valores de NaN y luego se imputaron mediante **interpolacion lineal respecto del tiempo**. Se eligió este método por las siguientes razones:                
1. Naturaleza de la variable: La temperatura es una variable continua con autocorrelación temporal; el valor de un día es muy similar al día anterior y al día siguiente. Por lo tanto el promedio ponderado de los vecinos es una estimación razonable del valor faltante. 
2. Baja proporción de faltantes: Los valores a imputar representan una fracción minima del total, por lo que el efecto de la distribución es acotado. 
3. Preservación de información: Eliminar las filas implicaria perder también los valores válidos de los demas variables en esos días y reducir la serie temporal. 
4. Superioridad sobre la media global: reemplazar por la media anual ignoraria la estacionalidad (un faltante en invierno recibiria un valor de verano) y distorsionaria la varianza. 
Para evitar imputaciones poco fiables se limito la interpolación a huecos de hasta 3 días consecutivos **limit=3** y no se estrapolo en los extremos de la serie **limit_area='inside'**. 

## ¿Por qué no eliminar registros?
Al eliminar aquellos registros que no son válidos se pierde la continuidad temporal lo que genera problema al momento de analizar tendencia. 

## ¿Qué significa el **method='time'**?
Realiza la ponderación teniendo en cuenta la distancia relativa de la fecha y no las distancia absoluta.  

# Conclusiones
Los siguientes estadisticos se calcularon sobre los datos original, sin tratamiento, con el fin de detectar anomalia. No deben interpretarse como resultado final.En el conjunto de datos la variable **temp_max_c** tiene valores negativos (representarian eventos anomalos), la variable **humedad_pct** también contiene valores negativos, la variable **precipitacion_mm** tienen valores negativos que representan situación de anomalia. La variable **"estacion"** se puede omitir del análisis esto se debe a que contiene un único valor y no aporta mayor información.
