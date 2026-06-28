import pandas as pd
import json

anexoa = pd.read_csv("AnexoA.csv")
incidentes_nuevos = pd.read_csv("incidents_master-selected-columns.csv")

def limpiar(df):
    Q1 = df["Registros"].quantile(0.25)
    Q3 = df["Registros"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df_resultado = df[(df["Registros"] >= limite_inferior) & (df["Registros"] <= limite_superior)]

    Q1 = df_resultado["Dias_Deteccion"].quantile(0.25)
    Q3 = df_resultado["Dias_Deteccion"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df_resultado = df_resultado[(df_resultado["Dias_Deteccion"] >= limite_inferior) & (df_resultado["Dias_Deteccion"] <= limite_superior)]
    return df_resultado

def formato_incidentes(df):
    df["fecha_inicio"] = pd.to_datetime(df["incident_date"], format="%Y-%m-%d")
    df["fecha_fin"] = pd.to_datetime(df["discovery_date"], format="%Y-%m-%d")
    df["dias_deteccion"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days

    with open('sectores.json', 'r', encoding='utf-8') as f:
        sectores = json.load(f)
        df['industry_primary'] = df['industry_primary'].map(sectores)
    df = df.drop(columns=['incident_date', 'discovery_date', "fecha_inicio", "fecha_fin"])
    df['attack_vector_primary'] = df['attack_vector_primary'].str.capitalize()
    df = df[['industry_primary','attack_vector_primary','dias_deteccion','data_compromised_records']]
    df.columns = ['Sector', 'Tipo', 'Dias_Deteccion', 'Registros']
    return df
    
def combinar(df1, df2):
    df_lista = [df1, df2]
    df_combinado = pd.concat(df_lista, ignore_index=True)
    return df_combinado

def dataset_encode(df):
    with open('codigos_s.json', 'r', encoding='utf-8') as f:
        codigos = json.load(f)
        df['Sector'] = df['Sector'].map(codigos)
    with open('codigos_t.json', 'r', encoding='utf-8') as f:
        codigos = json.load(f)
        df['Tipo'] = df['Tipo'].map(codigos)
    return df

incidentes_nuevos = formato_incidentes(incidentes_nuevos)

df_combinado = combinar(anexoa, incidentes_nuevos)
df_combinado.to_csv('dataset_raw.csv', index=False)
print("Base de datos completa guardada como dataset_raw.csv")
df_combinado = limpiar(df_combinado)
df_combinado.to_csv('dataset.csv', index=False)
print("Base de datos limpia y homóloga guardada como dataset.csv")
df_encoded = dataset_encode(df_combinado)
df_encoded.to_csv('dataset_encoded.csv', index=False)
print("Base de datos en codigo guardada como dataset_encoded.csv")
