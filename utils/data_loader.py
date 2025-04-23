import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    # Chargement du référentiel géographique
    df_geo = pd.read_csv("data/referentiel_geographique.csv", sep=";", on_bad_lines='skip')
    df_geo = df_geo[df_geo["geolocalisation"].notna()]
    df_geo["Latitude"] = df_geo["geolocalisation"].apply(lambda x: float(x.split(",")[0]))
    df_geo["Longitude"] = df_geo["geolocalisation"].apply(lambda x: float(x.split(",")[1]))
    df_geo["Nom"] = df_geo["COM_NOM_MAJ_COURT"].str.title()
    df_geo["Département"] = df_geo["DEP_NOM"]
    df_geo["Région"] = df_geo["REG_NOM"]
    df_geo["COM_CODE"] = df_geo["COM_CODE"].astype(str)

    # Chargement des données de population
    df_pop = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5, dtype=str)
    df_pop = df_pop.rename(columns={"CODGEO": "COM_CODE", "PMUN2022": "Population"})
    df_pop["COM_CODE"] = df_pop["COM_CODE"].astype(str)
    df_pop["Population"] = df_pop["Population"].str.replace(",", ".").astype(float)

    # Fusion des deux sources
    df = df_geo.merge(df_pop[["COM_CODE", "Population"]], on="COM_CODE", how="left")

    # Filtrage : uniquement communes > 20 000 habitants
    df = df[df["Population"] > 20000].copy()

    return df
