import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    # 🔹 Charger les populations INSEE
    df_pop = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)
    df_pop["COM_CODE"] = df_pop["CODGEO"].astype(str).str.zfill(5)
    df_pop["PMUN2022"] = df_pop["PMUN2022"].astype(str).str.replace(" ", "").str.replace(",", ".")
    df_pop["PMUN2022"] = pd.to_numeric(df_pop["PMUN2022"], errors="coerce")
    df_pop = df_pop[df_pop["PMUN2022"] > 20000]
    df_pop = df_pop[["COM_CODE", "LIBGEO", "PMUN2022"]]
    df_pop.rename(columns={"LIBGEO": "Nom", "PMUN2022": "Population"}, inplace=True)
    df_pop["Nom"] = df_pop["Nom"].str.title()

    # 🔹 Charger le référentiel géographique
    df_geo = pd.read_csv("data/referentiel_geographique.csv", sep=";", on_bad_lines='skip')
    df_geo = df_geo[df_geo["geolocalisation"].notna()]
    df_geo["COM_CODE"] = df_geo["COM_CODE"].astype(str).str.zfill(5)
    df_geo["Latitude"] = df_geo["geolocalisation"].apply(lambda x: float(x.split(",")[0]))
    df_geo["Longitude"] = df_geo["geolocalisation"].apply(lambda x: float(x.split(",")[1]))
    df_geo["Département"] = df_geo["DEP_NOM"]
    df_geo["Région"] = df_geo["REG_NOM"]

    # 🔹 Fusion des deux bases
    df = pd.merge(df_pop, df_geo, on="COM_CODE", how="left")

    # 🔹 Nettoyage final
    df = df[["COM_CODE", "Nom", "Population", "Département", "Région", "Latitude", "Longitude"]]

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
