import pandas as pd
import streamlit as st

VILLES_20K_HAB = [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg",
    "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Saint-Étienne",
    "Toulon", "Le Havre", "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne",
    "Clermont-Ferrand", "Saint-Denis", "La Rochelle", "Avignon", "Poitiers",
    "Pau", "Cannes", "Aix-en-Provence", "Amiens", "Orléans", "Boulogne-Billancourt",
    "Metz", "Rouen", "Besançon", "Perpignan", "Nancy", "Versailles", "Colombes",
    "Mulhouse", "Roubaix", "Tourcoing", "Montreuil", "Argenteuil", "Caen",
    "Saint-Paul", "Saint-Pierre", "Le Tampon", "Fort-de-France", "Saint-Louis",
    "Cholet", "Quimper", "La Roche-sur-Yon"
    # (Complète cette liste avec toutes les villes >20k si tu veux toutes les intégrer)
]

@st.cache_data
def load_city_data():
    df = pd.read_csv("data/referentiel_geographique.csv", sep=";", on_bad_lines='skip')

    # Nettoyage
    df = df[df["geolocalisation"].notna()]
    df["Latitude"] = df["geolocalisation"].apply(lambda x: float(x.split(",")[0]))
    df["Longitude"] = df["geolocalisation"].apply(lambda x: float(x.split(",")[1]))
    df["Nom"] = df["COM_NOM_MAJ_COURT"].str.title()
    df["Département"] = df["DEP_NOM"]
    df["Région"] = df["REG_NOM"]
    df["COM_CODE"] = df["COM_CODE"].astype(str)

    # Filtrage manuel : ne garder que les villes dans la liste
    df = df[df["Nom"].isin(VILLES_20K_HAB)]

    # Ajout d'une population factice pour le moment (tu peux mettre une vraie colonne si dispo plus tard)
    df["Population"] = 20000 + (df.index % 15000)

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
