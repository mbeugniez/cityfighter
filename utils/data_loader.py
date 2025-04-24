import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    # Chargement de la base
    df = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)

    # Nettoyage du nom de commune
    df["Nom"] = df["LIBGEO"].str.title()

    # Nettoyage de la colonne population 2022
    df["PMUN2022"] = df["PMUN2022"].astype(str).str.replace(" ", "").str.replace(",", ".")
    df["PMUN2022"] = pd.to_numeric(df["PMUN2022"], errors="coerce")

    # Filtrage des communes de plus de 20 000 habitants
    df = df[df["PMUN2022"] > 20000].copy()

    # Création du code commune en chaîne de caractères
    df["COM_CODE"] = df["CODGEO"].astype(str)
    df["Population"] = df["PMUN2022"]

    # On conserve les colonnes utiles
    colonnes_utiles = ["COM_CODE", "Nom", "Population", "DEP", "REG", "LIBGEO"]
    return df[colonnes_utiles]

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
