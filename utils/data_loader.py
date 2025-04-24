import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    df = pd.read_csv("data/referentiel_plus_20000.csv", sep=",")
    df = df[df["geolocalisation"].notna()]
    df["Latitude"] = df["geolocalisation"].apply(lambda x: float(x.split(",")[0]))
    df["Longitude"] = df["geolocalisation"].apply(lambda x: float(x.split(",")[1]))
    df["Nom"] = df["COM_NOM_MAJ_COURT"].str.title()
    df["Département"] = df["DEP_NOM"]
    df["Région"] = df["REG_NOM"]
    df["Population"] = df["PMUN2022"]
    df["COM_CODE"] = df["COM_CODE"].astype(str)
    return df

def get_city_info(df, city_name):
    row = df[df["Nom"] == city_name]
    if row.empty:
        return None  # <- ville non trouvée
    row = row.iloc[0]
    return {
        "Nom": row["Nom"],
        "Département": row["Département"],
        "Région": row["Région"],
        "Latitude": row["Latitude"],
        "Longitude": row["Longitude"],
        "Population": row["Population"],
        "COM_CODE": row["COM_CODE"]
    }
