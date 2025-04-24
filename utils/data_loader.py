import pandas as pd
import streamlit as st

@st.cache_data
def load_city_data():
    # Chargement de la base population réelle
    df = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)
    
    # Nettoyage des données de population
    df["PMUN2022"] = df["PMUN2022"].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)
    
    # Liste filtrée des villes de +20 000 habitants
    villes_autorisees = [
        "TOULOUSE", "BORDEAUX", "MONTPELLIER", "NICE", "MARSEILLE", "LYON", "LILLE",
        "NANTES", "RENNES", "ANGERS", "ROUEN", "LE HAVRE", "REIMS", "GRENOBLE", "DIJON",
        "ORLÉANS", "STRASBOURG", "CLERMONT-FERRAND", "LE MANS", "AMIENS", "BESANÇON",
        "BREST", "TOURS", "PERPIGNAN", "PAU", "BAYONNE", "DUNKERQUE", "AVIGNON",
        "NÎMES", "ANTIBES", "CANNES", "CAGNES-SUR-MER", "AJACCIO", "LA ROCHELLE",
        "CHÂLONS-EN-CHAMPAGNE", "CHÂTEAUROUX", "CHERBOURG-EN-COTENTIN", "TROYES", "BÉZIERS",
        "SAINT-ÉTIENNE", "VILLEURBANNE", "VALENCE", "MULHOUSE", "MÉTROPOLE DE LYON", 
        "SAINT-DENIS", "CREIL", "DOUAI", "SAINT-QUENTIN", "ALBI", "MONT-DE-MARSAN"
        # tu peux continuer à compléter ici en copiant la liste extraite plus haut
    ]
    
    df = df[df["LIBGEO"].str.upper().isin(villes_autorisees)]
    df["Nom"] = df["LIBGEO"].str.title()
    df["Département"] = df["DEP"]
    df["Région"] = df["REG"]
    df["Population"] = df["PMUN2022"].astype(int)
    df["COM_CODE"] = df["CODGEO"].astype(str)
    
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
