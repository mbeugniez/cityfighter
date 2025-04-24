import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    # Chargement du fichier INSEE
    df = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)

    # Création des colonnes utiles
    df["COM_CODE"] = df["CODGEO"].astype(str)
    df["Nom"] = df["LIBGEO"].str.title()

    # Nettoyage et conversion de la population 2022
    df["PMUN2022"] = df["PMUN2022"].astype(str).str.replace(" ", "").str.replace(",", ".")
    df["Population"] = pd.to_numeric(df["PMUN2022"], errors="coerce")

    # Filtrage des communes avec + de 20 000 habitants
    df = df[df["Population"] > 20000]

    # Colonnes factices pour compatibilité de l'appli
    df["Département"] = df.get("DEP", "Inconnu")
    df["Région"] = df.get("REG", "Inconnue")
    df["Latitude"] = np.nan
    df["Longitude"] = np.nan

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
