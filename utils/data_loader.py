import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    df = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)

    # Nettoyage du code commune
    df["COM_CODE"] = df["CODGEO"].astype(str).str.zfill(5)

    # Nettoyage de la population 2022
    df["PMUN2022"] = df["PMUN2022"].astype(str).str.replace(" ", "").str.replace(",", ".")
    df["PMUN2022"] = pd.to_numeric(df["PMUN2022"], errors="coerce")

    # Filtrage des communes avec plus de 20 000 habitants
    df = df[df["PMUN2022"] > 20000]

    # Préparation des colonnes
    df["Nom"] = df["LIBGEO"].str.title()
    df["Département"] = "Donnée indisponible"
    df["Région"] = "Donnée indisponible"
    df["Latitude"] = None  # ou coordonnées fictives si besoin
    df["Longitude"] = None
    df["Population"] = df["PMUN2022"]

    return df[["COM_CODE", "Nom", "Population", "Département", "Région", "Latitude", "Longitude"]]

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
