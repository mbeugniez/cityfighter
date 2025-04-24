import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    # 1. Chargement du fichier géographique
    df_geo = pd.read_csv("data/referentiel_geographique.csv", sep=";", on_bad_lines='skip')
    df_geo = df_geo[df_geo["geolocalisation"].notna()]
    df_geo["COM_CODE"] = df_geo["COM_CODE"].astype(str).str.zfill(5)
    df_geo["Nom"] = df_geo["COM_NOM_MAJ_COURT"].str.title()
    df_geo = df_geo[["COM_CODE", "Nom", "DEP_NOM", "REG_NOM", "geolocalisation"]]
    df_geo.rename(columns={"DEP_NOM": "Département", "REG_NOM": "Région"}, inplace=True)

    # 2. Chargement du fichier population
    df_pop = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)
    df_pop["COM_CODE"] = df_pop["CODGEO"].astype(str).str.zfill(5)  # Important !!
    df_pop["PMUN2022"] = df_pop["PMUN2022"].astype(str).str.replace(" ", "").str.replace(",", ".")
    df_pop["PMUN2022"] = pd.to_numeric(df_pop["PMUN2022"], errors="coerce")

    # 3. Filtrage des communes > 20 000 habitants
    df_pop = df_pop[df_pop["PMUN2022"] > 20000]

    # 4. Fusion sur le bon code
    df = df_geo.merge(df_pop[["COM_CODE", "PMUN2022"]], on="COM_CODE", how="inner")
    df.rename(columns={"PMUN2022": "Population"}, inplace=True)

    # 5. Extraction des coordonnées
    df["Latitude"] = df["geolocalisation"].apply(lambda x: float(x.split(",")[0]))
    df["Longitude"] = df["geolocalisation"].apply(lambda x: float(x.split(",")[1]))

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
