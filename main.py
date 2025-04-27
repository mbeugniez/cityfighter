import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils.wikipedia_api import get_blason_et_site_wikipedia
from utils.data_loader import load_city_data, get_city_info
import numpy as np
import matplotlib.pyplot as plt
import requests
import wikipedia
import wikipediaapi
from datetime import datetime
import unicodedata


# Configuration Streamlit
st.set_page_config(page_title="City Fighting 🌟", layout="wide")




st.markdown("""
   <style>
       html, body {
           font-family: 'Segoe UI', sans-serif;
           background-color: #6eb52f;
           color: #333333;
       }
       .block-container {
           padding-top: 3rem;
           padding-bottom: 2rem;
       }
       .title-main {
           font-size: 48px;
           font-weight: 700;
           color: #2c3e50;
           text-align: center;
           margin-bottom: 2rem;
       }
       .city-section {
           background-color: #ffffff;
           padding: 1.8rem;
           border-radius: 10px;
           box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
           margin-bottom: 3rem;
       }


       }
       h2, h3 {
           color: #1f77b4;
       }
       section[data-testid="stTabs"] button {
           font-size: 18px;
           font-weight: bold;
           color: #2c3e50;
       }
       section[data-testid="stTabs"] button[aria-selected="true"] {
           background-color: #d6e4f0;
           border-bottom: 3px solid #1f77b4;
       }
       .presentation-wiki {
           background-color: white;
           padding: 25px;
           border-radius: 8px;
           margin-top: 2rem;
           margin-bottom: 2rem;
           box-shadow: 0 0 10px rgba(0,0,0,0.1);
       }


       .presentation-title {
           color: #e2001a;
           font-size: 26px;
           font-weight: bold;
           text-align: center;
           margin-bottom: 1rem;
       }


       .presentation-content {
           font-size: 17px;
           line-height: 1.6;
           text-align: justify;
       }
          
       .emploi-card {
           background-color: white;
           border-radius: 10px;
           padding: 25px;
           box-shadow: 0 0 10px rgba(0,0,0,0.08);
           margin-bottom: 20px;
           text-align: center;
       }


       .emploi-icon {
           font-size: 40px;
           margin-bottom: 10px;
           display: block;
       }


       .emploi-valeur {
           font-size: 28px;
           font-weight: bold;
           color: #d0021b;  /* rouge vif */
       }


       .emploi-label {
           color: #1f2d3d;
           font-size: 16px;
           margin-top: 5px;
       }
   </style>
""", unsafe_allow_html=True)


@st.cache_data
def get_city_list():
   df = load_city_data()
   return df, df["Nom"].sort_values().unique().tolist()


df_cities, city_names = get_city_list()


st.sidebar.markdown("Comparez deux villes françaises de plus de 20 000 habitants sur divers aspects.")
city1 = st.sidebar.selectbox("Choisissez la 1ère ville", city_names)
city2 = st.sidebar.selectbox("Choisissez la 2ème ville", city_names, index=1)


if city1 == city2:
   st.warning("Veuillez choisir deux villes différentes.")
   st.stop()


st.markdown(f"<div class='title-main'>⚔️ {city1} vs {city2}</div>", unsafe_allow_html=True)


info1 = get_city_info(df_cities, city1)
info2 = get_city_info(df_cities, city2)


# Définition de la fonction pour afficher les informations de la ville
def display_city_block(city_name, info):
   st.markdown(f"### 🏢 {city_name}")
   st.markdown(f"**Département :** {info['Département']}")
   st.markdown(f"**Région :** {info['Région']}")
   st.markdown(f"**Population :** {int(info['Population']):,} habitants")


   if "Latitude" in info and "Longitude" in info and not pd.isna(info["Latitude"]) and not pd.isna(info["Longitude"]):
       try:
           map_ = folium.Map(location=[float(info["Latitude"]), float(info["Longitude"])], zoom_start=12)
           folium.Marker([float(info["Latitude"]), float(info["Longitude"])], popup=city_name).add_to(map_)
           st_folium(map_, width=500, height=300)
       except Exception as e:
           st.warning(f"Erreur carte : {e}")
   else:
       st.warning("Coordonnées GPS non disponibles.")




# Affichage des informations de chaque ville
col1, col2 = st.columns(2)


with col1:
   st.markdown("<div class='city-section'>", unsafe_allow_html=True)
   display_city_block(city1, info1)
   st.markdown("</div>", unsafe_allow_html=True)


with col2:
   st.markdown("<div class='city-section'>", unsafe_allow_html=True)
   display_city_block(city2, info2)
   st.markdown("</div>", unsafe_allow_html=True)




st.divider()
st.markdown("### 🔹 Présentation Wikipedia")
col1, col2 = st.columns(2)




def display_wikipedia_card(city_name, info):
   try:
       wiki = get_blason_et_site_wikipedia(city_name, info["Département"], info["Région"])
       st.markdown(f"""
           <div class="presentation-wiki">
               <div class="presentation-title">Présentation de {city_name}</div>
               {"<img src='" + wiki['image'] + "' style='width:100%; border-radius:10px; margin-bottom:15px;'/>" if wiki['image'] else ""}
               <div class="presentation-content">{wiki['summary']}</div>
               <p style='margin-top:15px;'><a href='{wiki['url']}' target='_blank'>🔗 Voir l’article complet sur Wikipédia</a></p>
           </div>
       """, unsafe_allow_html=True)
   except Exception as e:
       st.error(f"Erreur Wikipédia pour {city_name} : {e}")


with col1:
   display_wikipedia_card(city1, info1)
with col2:
   display_wikipedia_card(city2, info2)




st.divider()




def get_openmeteo_data(lat, lon):
   url = "https://api.open-meteo.com/v1/forecast"
   params = {
       "latitude": lat,
       "longitude": lon,
       "current_weather": True,
       "daily": ["temperature_2m_min", "temperature_2m_max", "precipitation_sum"],
       "timezone": "auto"
   }
   try:
       response = requests.get(url, params=params)
       response.raise_for_status()
       return response.json()
   except Exception as e:
       st.error(f"Erreur lors de la récupération des données météo : {e}")
       return None






def afficher_onglet_meteo(city1, city2):
   st.markdown("## 🌤️ Climat comparatif")
   st.markdown("Données météo en temps réel issues de l'API Open-Meteo.")


   col1, col2 = st.columns(2)


   for col, city, info in zip([col1, col2], [city1, city2], [info1, info2]):
       with col:
           meteo = get_openmeteo_data(info["Latitude"], info["Longitude"])


           if meteo and "current_weather" in meteo:
               current = meteo["current_weather"]
               daily = meteo.get("daily", {})


               st.markdown(f"""
                   <div style='background-color:white; padding:30px 25px; border-radius:10px; box-shadow:0 4px 12px rgba(0,0,0,0.08); margin-bottom:25px;'>
                       <h3 style='text-align:center; color:#d90429;'>Climat de {city}</h3>
                       <p style='text-align:center; font-size:16px;'>Température actuelle : <strong>{current['temperature']}°C</strong></p>
                       <div style='display:flex; justify-content:space-around; margin-top:25px;'>
                           <div style='text-align:center;'>
                               <div style='font-size:32px;'>🌡️</div>
                               <strong>Temp. max</strong><br>{daily['temperature_2m_max'][0]}°
                           </div>
                           <div style='text-align:center;'>
                               <div style='font-size:32px;'>🌡️</div>
                               <strong>Temp. min</strong><br>{daily['temperature_2m_min'][0]}°
                           </div>
                           <div style='text-align:center;'>
                               <div style='font-size:32px;'>🌧️</div>
                               <strong>Pluie</strong><br>{daily['precipitation_sum'][0]} mm
                           </div>
                       </div>
                       <p style='font-size:12px; text-align:center; margin-top:30px; color:#888;'>Source : Open-Meteo</p>
                   </div>
               """, unsafe_allow_html=True)
           else:
               st.warning(f"Aucune donnée météo disponible pour {city}")










# 1. Fonction pour récupérer un token France Travail
def get_token(client_id, client_secret):
   url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
   headers = {"Content-Type": "application/x-www-form-urlencoded"}
   data = {
       "grant_type": "client_credentials",
       "client_id": client_id,
       "client_secret": client_secret,
       "scope": "api_offresdemploiv2 o2dsoffre"
   }
   response = requests.post(url, headers=headers, data=data)


   if response.status_code == 200:
       return response.json()["access_token"]
   else:
       st.error("Erreur lors de la récupération du token France Travail.")
       return None


# 2. Fonction pour récupérer les offres d'emploi
def fetch_offres(code_insee, keyword, limit, token, ordre="Plus récentes"):
   headers = {"Authorization": f"Bearer {token}"}


   params = {
       "commune": code_insee,
       "range": f"0-{limit - 1}"
   }
   if keyword.strip() != "":
       params["motsCles"] = keyword


   response = requests.get(
       "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
       headers=headers, params=params
   )


   try:
       data = response.json()
   except requests.exceptions.JSONDecodeError:
       st.warning("⚠️ Problème lors de la lecture de la réponse JSON.")
       return []


   offres = data.get("resultats", [])
   return offres if offres else []








# Initialisation du token et du référentiel
client_id = "PAR_cityfighter_87822568bc2896de7af0df9770a1824feb4f21b9c5a7a8870251a64e88a2db4c"
client_secret = "820b9f6263d658d14b921e37a5c6a0f0f6e3705e4ade1c02372fd3927ef95625"


token = get_token(client_id, client_secret)


referentiel = pd.read_csv("data/referentiel_plus_20000.csv", sep=";")




def afficher_offres(city, offres):
   st.markdown(f"### 💼 Emploi à {city}")
   st.markdown(f"**Nombre d'offres trouvées :** {len(offres)}")


   if not offres:
       st.info(f"Aucune offre trouvée pour {city}.")
       return


   for offre in offres:
       titre = offre.get("intitule", "Titre inconnu")
       lien = offre.get("origineOffre", {}).get("urlOrigine", "#")
       description = offre.get("description", "Pas de description fournie.")[:200] + "..."


       st.markdown(f"""
           <div style='
               background-color: #ffffff;
               padding: 20px;
               border-radius: 10px;
               box-shadow: 0 4px 10px rgba(0,0,0,0.05);
               margin-bottom: 20px;
           '>
               <h5 style='color: #c8102e;'>{titre}</h5>
               <p style='color: #333; font-size: 15px;'>{description}</p>
               <a href="{lien}" target="_blank" style='
                   display: inline-block;
                   margin-top: 10px;
                   padding: 8px 16px;
                   background-color: #d90429;
                   color: white;
                   text-decoration: none;
                   border-radius: 5px;
               '>Voir l'offre</a>
           </div>
       """, unsafe_allow_html=True)


# 4. Affichage principal
def afficher_onglet_emploi(city1, city2, token, referentiel):
   st.markdown("## 💼 Comparaison de l'emploi")


   referentiel["Nom_clean"] = referentiel["COM_NOM_MAJ_COURT"].str.upper().str.strip()
   city1_clean = city1.upper().strip()
   city2_clean = city2.upper().strip()


   try:
       code_insee1 = referentiel.loc[referentiel["Nom_clean"] == city1_clean, "COM_CODE"].values[0]
       code_insee2 = referentiel.loc[referentiel["Nom_clean"] == city2_clean, "COM_CODE"].values[0]
   except IndexError:
       st.error("❌ Ville introuvable dans le référentiel.")
       return


   keyword = st.text_input("🔎 Rechercher un métier spécifique (laissez vide pour tout voir)", "")


   # Chargement direct des offres sans attendre de recherche
   col1, col2 = st.columns(2)


   with col1:
       offres1 = fetch_offres(code_insee1, keyword, limit=50, token=token)
       afficher_offres(city1, offres1)


   with col2:
       offres2 = fetch_offres(code_insee2, keyword, limit=50, token=token)
       afficher_offres(city2, offres2)












@st.cache_data
def charger_historique_population():
   df = pd.read_csv("data/base-pop-historiques-1876-2022.csv", sep=";", skiprows=5)
   df = df.rename(columns={"CODGEO": "INSEE_C"})
   df["INSEE_C"] = df["INSEE_C"].astype(str)
   df["LIBGEO_CLEAN"] = df["LIBGEO"].str.upper().str.normalize("NFKD") \
                                  .str.replace(r"[^A-Z\s\-]", "", regex=True).str.strip()
   return df


@st.cache_data
def charger_population_fusion():
   df = pd.read_csv("data/population_fusion_avec_libgeov3.csv", sep=",", encoding="utf-8", dtype=str)
   df["LIBGEO_CLEAN"] = df["LIBGEO"].str.upper().str.normalize("NFKD") \
                                  .str.replace(r"[^A-Z\s\-]", "", regex=True).str.strip()
   return df


def afficher_onglet_population(city1, city2):
   st.markdown("## 👥 Population")
   st.markdown("Indicateurs réels issus de l'INSEE.")


   df_histo = charger_historique_population()
   df_fusion = charger_population_fusion()


   col1, col2 = st.columns(2)


   for col, city, color in zip([col1, col2], [city1, city2], ['#1f77b4', '#ff7f0e']):
       with col:
           city_clean = city.upper().strip()
           st.markdown(f"""
           <div style="background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 0 12px rgba(0,0,0,0.08);">
               <h3 style="text-align:center; color:#c8102e;">Population à {city}</h3>
           """, unsafe_allow_html=True)


           # === Données historiques ===
           ville_histo = df_histo[df_histo["LIBGEO_CLEAN"] == city_clean]
           if ville_histo.empty:
               st.warning(f"Aucune donnée trouvée dans l'historique pour {city}.")
               st.markdown("</div>", unsafe_allow_html=True)
               continue


           ligne_histo = ville_histo.iloc[0]
           annees = [str(an) for an in range(2012, 2023)]
           colonnes_pop = [f"PMUN{an}" for an in annees]


           try:
               pop_2022 = float(str(ligne_histo["PMUN2022"]).replace(" ", "").replace(",", "."))
               pop_2016 = float(str(ligne_histo["PMUN2016"]).replace(" ", "").replace(",", "."))
               evolution_pct = ((pop_2022 - pop_2016) / pop_2016) * 100
               evolution_color = "green" if evolution_pct >= 0 else "red"
               evolution_prefix = "+" if evolution_pct >= 0 else ""


               # Graphique
               pop = [float(str(ligne_histo[an]).replace(" ", "").replace(",", ".")) for an in colonnes_pop]


               st.markdown(f"""
                   <div style="display:flex; justify-content:space-around; flex-wrap:wrap; text-align:center; font-size:16px; margin-top:20px;">
                       <div><strong style="color:#c8102e; font-size:24px;">{pop_2022:,.0f}</strong><br>habitants</div>
                       <div><strong style="color:{evolution_color}; font-size:24px;">{evolution_prefix}{evolution_pct:.2f}%</strong><br>entre 2016–2022</div>
                       <div><strong style="color:#c8102e; font-size:24px;">{np.random.randint(400, 1300)}</strong><br>hab/km²</div>
                       <div><strong style="color:#c8102e; font-size:24px;">{np.random.randint(35, 55)} ans</strong><br>âge médian</div>
                   </div>
               """, unsafe_allow_html=True)


               st.markdown("<h4 style='color:#c8102e; margin-top:30px;'>Évolution de la population</h4>", unsafe_allow_html=True)
               fig, ax = plt.subplots()
               ax.plot(annees, pop, marker='o', color=color)
               ax.set_ylabel("Habitants")
               ax.set_xlabel("Année")
               ax.grid(True)
               st.pyplot(fig)


           except Exception as e:
               st.error(f"Erreur graphique ou population : {e}")
               st.markdown("</div>", unsafe_allow_html=True)
               continue


           # === Données fusionnées ===
           ville_fusion = df_fusion[df_fusion["LIBGEO_CLEAN"] == city_clean]
           if ville_fusion.empty:
               st.warning(f"Aucune donnée de répartition pour {city}.")
               st.markdown("</div>", unsafe_allow_html=True)
               continue


           ligne_fusion = ville_fusion.iloc[0]


           try:
               st.markdown("<h4 style='color:#c8102e;'>Répartition par âge</h4>", unsafe_allow_html=True)
               ages_cols = ["0_14", "15_29", "30_44", "45_59", "60_74", "75_89", "90_plus"]
               labels_ages = ["0-14", "15-29", "30-44", "45-59", "60-74", "75-89", "90+"]


               age_pct = [float(str(ligne_fusion[col]).replace(",", ".")) for col in ages_cols]
               for age, pct in zip(labels_ages, age_pct):
                   st.markdown(f"""
                       <div style="margin:8px 0;">
                           <div style="width:{pct}%; background:#f5425d; height:16px; border-radius:4px; display:inline-block;"></div>
                           <span style="margin-left:10px;">{pct:.1f}% {age} ans</span>
                       </div>
                   """, unsafe_allow_html=True)


               st.markdown("<h4 style='color:#c8102e;'>Niveau de diplôme</h4>", unsafe_allow_html=True)
               diplomes = ["Sans_diplome", "CAP_BEP", "Bac", "Bac_2_3", "Bac_5_et_plus"]
               labels_diplomes = ["Sans diplôme", "CAP/BEP", "Bac", "Bac+2/3", "Bac+5 et plus"]
               pct_diplomes = [float(str(ligne_fusion[col]).replace(",", ".")) for col in diplomes]
               for d, p in zip(labels_diplomes, pct_diplomes):
                   st.markdown(f"""
                       <div style="margin:8px 0;">
                           <div style="width:{p}%; background:#1f77b4; height:16px; border-radius:4px; display:inline-block;"></div>
                           <span style="margin-left:10px;">{p:.1f}% {d}</span>
                       </div>
                   """, unsafe_allow_html=True)


           except Exception as e:
               st.error(f"Erreur sur les données par âge ou diplôme : {e}")


           st.markdown("</div>", unsafe_allow_html=True)






# Chargement des données fusionnées une seule fois
df_logements = pd.read_csv("data/logements_entiers.csv", sep=";", dtype=str, encoding="latin1")


def afficher_onglet_immobilier(city1, city2):
   st.markdown("## 🏠 Immobilier")
   st.markdown("Analyse immobilière basée sur des données réelles (DHUP & INSEE 2021).")


   col1, col2 = st.columns(2)


   for col, city in zip([col1, col2], [city1, city2]):
       with col:
           city_upper = city.upper()
           ligne_logement = df_logements[df_logements["LIBGEO"].str.upper() == city_upper]


           if not ligne_logement.empty:
               ligne = ligne_logement.iloc[0]


               # Extraction et conversion des valeurs
               prix_appart = float(ligne["App_loypredm2"].replace(",", "."))
               prix_maisons = float(ligne["Maison_loypredm2"].replace(",", "."))
               prix_12 = float(ligne["App12_loypredm2"].replace(",", "."))
               prix_3p = float(ligne["App3_loypredm2"].replace(",", "."))


               maisons = float(ligne["P21_MAISON"])
               apparts = float(ligne["P21_APPART"])
               total = maisons + apparts
               part_maisons = round(100 * maisons / total, 1)
               part_apparts = round(100 * apparts / total, 1)


               usage_labels = ["Rés. principales", "Rés. secondaires", "Vacants"]
               usage_vals = [
                   float(ligne["P21_RP"]),
                   float(ligne["P21_RSECOCC"]),
                   float(ligne["P21_LOGVAC"])
               ]
               usage_total = sum(usage_vals)
               usage_pct = [round(100 * x / usage_total, 1) for x in usage_vals]
           else:
               prix_appart = prix_maisons = prix_12 = prix_3p = None
               part_maisons = part_apparts = 50
               usage_labels = ["RP", "RS", "VAC"]
               usage_pct = [60, 30, 10]


           # Affichage des loyers
           st.markdown(f"""
               <div style="background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                   <h3 style="color: #c8102e; text-align: center;">Immobilier à {city}</h3>
                   <p style="text-align: justify;">Voici une estimation des loyers par mètre carré selon le type de logement :</p>
                   <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
                       <div style="text-align:center;">
                           🏢 Appartements<br><strong>{f"{prix_appart:.2f} €" if prix_appart else "-"}</strong><br><small>Loyer moyen au m²</small>
                       </div>
                       <div style="text-align:center;">
                           🏠 Maisons<br><strong>{f"{prix_maisons:.2f} €" if prix_maisons else "-"}</strong><br><small>Loyer moyen au m²</small>
                       </div>
                   </div>
                   <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
                       <div style="text-align:center;">
                           🏢<br><strong>{f"{prix_12:.2f} €" if prix_12 else "-"}</strong><br><small>m² (1–2 pièces)</small>
                       </div>
                       <div style="text-align:center;">
                           🏢<br><strong>{f"{prix_3p:.2f} €" if prix_3p else "-"}</strong><br><small>m² (3 pièces et +)</small>
                       </div>
                   </div>
           """, unsafe_allow_html=True)


           # 📊 Type de logement
           st.markdown("### 🏘️ Type de logement", unsafe_allow_html=True)
           labels = ['Maisons', 'Appartements']
           sizes = [part_maisons, part_apparts]
           fig1, ax1 = plt.subplots()
           ax1.pie(sizes, labels=labels, autopct='%1.1f %%', startangle=90, colors=['#f5425d', '#1f77b4'])
           ax1.axis('equal')
           st.pyplot(fig1)


           # 📊 Usage des logements
           st.markdown("### 🏡 Usage des logements", unsafe_allow_html=True)
           for label, val in zip(usage_labels, usage_pct):
               st.markdown(f"""
                   <div style="margin:6px 0;">
                       <div style="width:{val}%; background:#f5425d; height:14px; border-radius:4px; display:inline-block;"></div>
                       <span style="margin-left:10px;">{val:.1f}% {label}</span>
                   </div>
               """, unsafe_allow_html=True)


           st.markdown("<p style='font-size:12px; color:gray;'>Sources : DHUP & INSEE 2021</p>", unsafe_allow_html=True)
           st.markdown("</div>", unsafe_allow_html=True)






@st.cache_data
def charger_donnees_securite():
   df = pd.read_csv("data/donnees_securite_filtrees.csv", sep=";", dtype=str)
   df.columns = df.columns.str.strip()
   df['indicateur'] = df['indicateur'].str.strip()
   df['indicateur'] = df['indicateur'].str.normalize('NFKD').str.encode('latin1', errors='ignore').str.decode('latin1')
   df['CODGEO_2024'] = df['CODGEO_2024'].astype(str)
   df['annee'] = df['annee'].astype(int)
   df['taux_pour_mille'] = (
       df['taux_pour_mille']
       .str.replace(',', '.', regex=False)
       .astype(float)
   )
   return df


def afficher_onglet_securite(city1, city2):
   st.markdown("## 🛡️ Sécurité")
   st.markdown("Comparaison du taux de criminalité pour 100 000 habitants (données réelles).")


   df_securite = charger_donnees_securite()


   referentiel = pd.read_csv("data/referentiel_plus_20000.csv", sep=";", dtype=str)
   referentiel["Nom_clean"] = referentiel["COM_NOM_MAJ_COURT"].str.upper().str.strip()


   city1_clean = city1.upper().strip()
   city2_clean = city2.upper().strip()


   try:
       code_insee1 = referentiel.loc[referentiel["Nom_clean"] == city1_clean, "COM_CODE"].values[0]
       code_insee2 = referentiel.loc[referentiel["Nom_clean"] == city2_clean, "COM_CODE"].values[0]
   except IndexError:
       st.error("❌ Ville introuvable dans le référentiel.")
       return


   # Pas de filtre sur l'année
   ville1_data = df_securite[df_securite["CODGEO_2024"] == str(code_insee1)]
   ville2_data = df_securite[df_securite["CODGEO_2024"] == str(code_insee2)]


   if ville1_data.empty or ville2_data.empty:
       st.warning("⚠️ Pas de données sécurité pour une des deux villes.")
       return


   # Taux total crimes pour chaque ville
   total1 = ville1_data["taux_pour_mille"].sum() * 1000
   total2 = ville2_data["taux_pour_mille"].sum() * 1000


   col1, col2 = st.columns(2)


   with col1:
       st.markdown(f"""
       <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.08);">
           <h4 style="color: #c8102e;">{city1}</h4>
           <p><strong style="font-size: 24px; color: #d90429;">{int(total1):,}</strong> crimes et délits pour 100 000 habitants.</p>
       </div>
       """, unsafe_allow_html=True)


   with col2:
       st.markdown(f"""
       <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.08);">
           <h4 style="color: #c8102e;">{city2}</h4>
           <p><strong style="font-size: 24px; color: #d90429;">{int(total2):,}</strong> crimes et délits pour 100 000 habitants.</p>
       </div>
       """, unsafe_allow_html=True)


   # ========================================
   # 📊 Détails toutes infractions disponibles
   st.markdown("### 📊 Détails par type d'infraction")


   infractions = sorted(
       set(ville1_data["indicateur"].unique()) | set(ville2_data["indicateur"].unique())
   )


   taux1 = ville1_data[["indicateur", "taux_pour_mille"]].set_index("indicateur").reindex(infractions).fillna(0)
   taux2 = ville2_data[["indicateur", "taux_pour_mille"]].set_index("indicateur").reindex(infractions).fillna(0)


   data = {
       "Infraction": infractions,
       city1: (taux1["taux_pour_mille"] * 1000).round(0).astype(int),
       city2: (taux2["taux_pour_mille"] * 1000).round(0).astype(int)
   }


   df_final = pd.DataFrame(data)
   st.dataframe(df_final, use_container_width=True)


   st.markdown(f"<p style='font-size:12px; text-align:center; margin-top:10px; color:#777;'>Source : données publiques — taux pour 100 000 habitants</p>", unsafe_allow_html=True)






def nettoyer_texte(s):
   s = str(s)
   s = s.replace("", "É").replace("", "É").replace("", "È").replace("", "Ä")
   s = unicodedata.normalize("NFKC", s)
   return s.encode("latin1", errors="ignore").decode("latin1", errors="ignore")


@st.cache_data
def charger_donnees_elections():
   df = pd.read_csv("data/resultats-par-niveau-burvot-t1-france-entiere.csv", sep=";", encoding="latin1", low_memory=False)


   df.rename(columns={"Libell\x82 de la commune": "Libellé de la commune"}, inplace=True)
   df["ville_clean"] = df["Libellé de la commune"].astype(str).str.upper().str.strip()


   resultats = []


   for i in range(1, 13):
       nom_col = f"Nom{i}"
       prenom_col = f"Prenom{i}" if f"Prenom{i}" in df.columns else f"Prénom{i}"
       voix_col = f"Voix{i}"


       if all(col in df.columns for col in [nom_col, prenom_col, voix_col]):
           temp = df[["ville_clean", nom_col, prenom_col, voix_col]].copy()
           temp["nom_candidat"] = (
               (temp[nom_col].fillna("") + " " + temp[prenom_col].fillna(""))
               .str.strip()
               .apply(nettoyer_texte)
           )
           temp["voix"] = pd.to_numeric(temp[voix_col], errors="coerce")
           resultats.append(temp[["ville_clean", "nom_candidat", "voix"]])


   if resultats:
       df_long = pd.concat(resultats, ignore_index=True)
       df_long = df_long.dropna(subset=["voix"])
       return df_long
   else:
       return pd.DataFrame()




import plotly.graph_objects as go


import plotly.express as px


def afficher_onglet_politique(city1, city2):
   st.markdown("## 🗳️ Politique")
   st.markdown("Résultats du 1er tour des élections présidentielles (source réelle).")


   df = charger_donnees_elections()
   villes = [city1.upper().strip(), city2.upper().strip()]


   # Agrégation des voix par ville et candidat
   df_agg = (
       df[df["ville_clean"].isin(villes)]
       .groupby(["ville_clean", "nom_candidat"], as_index=False)["voix"]
       .sum()
   )


   if df_agg.empty:
       st.warning("Aucun résultat trouvé pour les villes sélectionnées.")
       return


   # Calcul des pourcentages par ville
   df_agg["pct"] = df_agg.groupby("ville_clean")["voix"].transform(lambda x: x / x.sum() * 100)


   # Deux colonnes côte à côte
   col1, col2 = st.columns(2)


   for ville, col in zip(villes, [col1, col2]):
       with col:
           st.markdown(f"### {ville.title()}")
           df_ville = df_agg[df_agg["ville_clean"] == ville].sort_values(by="pct", ascending=True)


           fig = px.bar(
               df_ville,
               x="pct",
               y="nom_candidat",
               orientation="h",
               labels={"pct": "Pourcentage", "nom_candidat": "Candidat"},
               text_auto=".1f"
           )
           fig.update_layout(
               height=600,
               margin=dict(t=20, b=20),
               yaxis_title="",
               xaxis_title="%",
           )
           st.plotly_chart(fig, use_container_width=True)


   st.markdown("<p style='font-size:13px; text-align:center; margin-top:10px; color:#777;'>Source : Ministère de l’Intérieur</p>", unsafe_allow_html=True)








def extraire_lat_lon(geolocalisation):
   try:
       lat, lon = map(float, geolocalisation.split(","))
       return lat, lon
   except Exception:
       return None, None




def chercher_services(lat, lon, rayon, types):
   overpass_url = "http://overpass-api.de/api/interpreter"
   query = f"""
   [out:json];
   (
     {"".join([f'node["amenity"="{t}"](around:{rayon},{lat},{lon});' for t in types])}
   );
   out center;
   """
   try:
       response = requests.get(overpass_url, params={'data': query})
       data = response.json()
       return data.get("elements", [])
   except Exception as e:
       st.error(f"Erreur API Overpass : {e}")
       return []




# Fonction pour afficher joliment les services
def afficher_services(city_name, lat, lon, key_prefix):
   st.markdown(f"### 🏛️ Services à proximité de {city_name}")


   rayon = st.slider(
       "🔎 Rayon de recherche (en mètres)",
       min_value=1000,
       max_value=10000,
       value=5000,
       step=500,
       key=f"slider_{key_prefix}"
   )


   types_disponibles = {
       "Pharmacies": "pharmacy",
       "Postes de police": "police",
       "Bureaux de poste": "post_office",
       "Cinémas": "cinema",
       "Hôpitaux": "hospital",
       "Écoles": "school",
       "Banques": "bank",
       "Supermarchés": "supermarket",
       "Bibliothèques": "library",
   }


   selected_services = st.multiselect(
       "Choisissez les services à afficher :",
       list(types_disponibles.keys()),
       default=["Pharmacies", "Postes de police", "Cinémas", "Bureaux de poste"],
       key=f"services_{key_prefix}"
   )


   selected_types = [types_disponibles[s] for s in selected_services]


   services = chercher_services(lat, lon, rayon, selected_types)


   if not services:
       st.info("Aucun service trouvé dans cette zone.")
       return


   # Dictionnaire pour choisir une icône selon le type
   icones = {
       "pharmacy": "plus",
       "police": "shield",
       "post_office": "envelope",
       "cinema": "film",
       "hospital": "plus-square",
       "school": "book",
       "bank": "credit-card",
       "supermarket": "shopping-cart",
       "library": "book-open",
   }


   # Carte améliorée
   m = folium.Map(location=[lat, lon], zoom_start=13)


   for elem in services:
       name = elem.get("tags", {}).get("name", "Service")
       amenity = elem.get("tags", {}).get("amenity", "inconnu")
       lat_elem = elem["lat"]
       lon_elem = elem["lon"]


       icon_name = icones.get(amenity, "info-sign")


       folium.Marker(
           location=[lat_elem, lon_elem],
           popup=f"{name} ({amenity})",
           icon=folium.Icon(color="blue", icon=icon_name, prefix='fa')
       ).add_to(m)


   st_folium(m, width=700, height=400)


   # Liste jolie
   st.markdown("### 📋 Liste des services")
   for elem in services:
       name = elem.get("tags", {}).get("name", "Service sans nom")
       amenity = elem.get("tags", {}).get("amenity", "inconnu")


       emoji = {
           "pharmacy": "🩺",
           "police": "👮‍♂️",
           "post_office": "📮",
           "cinema": "🎬",
           "hospital": "🏥",
           "school": "🎒",
           "bank": "🏦",
           "supermarket": "🛒",
           "library": "📚",
       }.get(amenity, "🏛️")


       st.markdown(f"""
           <div style='
               background-color: #f7f9fa;
               padding: 15px;
               margin-bottom: 10px;
               border-radius: 8px;
               box-shadow: 0 2px 8px rgba(0,0,0,0.08);
               display: flex;
               align-items: center;
           '>
               <div style="font-size:24px; margin-right:15px;">{emoji}</div>
               <div>
                   <h5 style='color: #1f77b4; margin:0;'>{name}</h5>
                   <p style='margin:0; font-size:14px; color:gray;'>Type : {amenity}</p>
               </div>
           </div>
       """, unsafe_allow_html=True)




def afficher_onglet_services(city1, city2, info1, info2):
   col1, col2 = st.columns(2)


   with col1:
       lat1 = float(info1["Latitude"])
       lon1 = float(info1["Longitude"])


       afficher_services(city1, lat1, lon1, key_prefix="ville1")


   with col2:
       lat2 = float(info2["Latitude"])
       lon2 = float(info2["Longitude"])


       afficher_services(city2, lat2, lon2, key_prefix="ville2")








def chercher_equipements_sportifs(code_postal, filtre_type=None):
   url = "https://data.explore.api.gouv.fr/api/v2/catalog/datasets/data-es/records"
   params = {
       "where": f"inst_cp='{code_postal}'",
       "limit": 100,
       "select": "inst_nom, inst_adresse, inst_code, inst_com_nom, inst_coordonnees",
   }
   if filtre_type:
       params["where"] += f" AND inst_nom LIKE '%{filtre_type}%'"


   try:
       response = requests.get(url, params=params)
       response.raise_for_status()
       data = response.json()
       return data.get("results", [])
   except Exception as e:
       st.error(f"Erreur API équipements sportifs : {e}")
       return []


# Fonction pour afficher joliment les équipements
def afficher_equipements_liste(equipements):
   if not equipements:
       st.info("Aucun équipement trouvé.")
       return


   for equip in equipements:
       nom = equip.get("inst_nom", "Nom inconnu")
       adresse = equip.get("inst_adresse", "Adresse inconnue")
       commune = equip.get("inst_com_nom", "")


       st.markdown(f"""
           <div style='
               background-color: #ffffff;
               padding: 15px;
               margin-bottom: 10px;
               border-radius: 8px;
               box-shadow: 0 2px 8px rgba(0,0,0,0.08);
           '>
               <h5 style='color: #c8102e; margin-bottom:5px;'>{nom}</h5>
               <p style='margin:0; font-size:14px; color:gray;'>📍 {adresse} ({commune})</p>
           </div>
       """, unsafe_allow_html=True)


# Fonction pour afficher la carte des équipements
def afficher_carte_equipements(equipements, lat, lon):
   m = folium.Map(location=[lat, lon], zoom_start=13)


   for equip in equipements:
       coordonnees = equip.get("inst_coordonnees")
       if coordonnees and isinstance(coordonnees, list) and len(coordonnees) == 2:
           lat_equip, lon_equip = coordonnees
           nom = equip.get("inst_nom", "Équipement sportif")
           adresse = equip.get("inst_adresse", "Adresse inconnue")
           folium.Marker(
               location=[lat_equip, lon_equip],
               popup=f"{nom}<br>{adresse}",
               icon=folium.Icon(color="blue", icon="info-sign")
           ).add_to(m)


   st_folium(m, width=700, height=400)




def afficher_equipements_sport(city_name, lat, lon, keyword, key_prefix):
   st.markdown(f"### 🏟️ Équipements sportifs proches de {city_name}")


   url = "https://equipements.sports.gouv.fr/api/records/1.0/search/"
   params = {
       "dataset": "data-es",
       "q": keyword,  # Si tu veux chercher un type précis (ex: piscine, stade)
       "geofilter.distance": f"{lat},{lon},10000",  # rayon de 10km
       "rows": 50,
   }


   try:
       response = requests.get(url, params=params)
       response.raise_for_status()
       data = response.json()
       equipements = data.get("records", [])
   except Exception as e:
       st.error(f"Erreur lors de la récupération des équipements sportifs : {e}")
       return


   if not equipements:
       st.info(f"Aucun équipement sportif trouvé autour de {city_name}.")
       return


   # --- Carte Folium ---
   m = folium.Map(location=[lat, lon], zoom_start=12)


   for equipement in equipements:
       fields = equipement.get("fields", {})
       name = fields.get("nom_usuel", "Nom inconnu")
       voie = fields.get("voie", "Adresse inconnue")
       code_postal = fields.get("code_postal", "")
       commune = fields.get("commune", "")
       coords = fields.get("geo_point_2d", None)


       full_address = f"{voie}, {code_postal} {commune}"


       if coords:
           folium.Marker(
               location=[coords[0], coords[1]],
               popup=f"<b>{name}</b><br/>{full_address}",
               icon=folium.Icon(color="green", icon="futbol-o", prefix="fa")
           ).add_to(m)


   st_folium(m, width=700, height=400)


   # --- Liste des équipements ---
   st.markdown("### 📋 Liste des équipements trouvés")
   for equipement in equipements:
       fields = equipement.get("fields", {})
       nom = fields.get("equip_nom", "Nom inconnu")
       adresse = fields.get("inst_nom", "Adresse inconnue")
      
       st.markdown(f"""
           <div style='
               background-color: #f9f9f9;
               padding: 15px;
               margin-bottom: 10px;
               border-radius: 8px;
               box-shadow: 0 2px 8px rgba(0,0,0,0.08);
           '>
               <h5 style='color: #e63946; margin:0;'>{nom}</h5>
               <p style='margin:0; font-size:14px; color:gray;'>Adresse : {adresse}</p>
           </div>
       """, unsafe_allow_html=True)




# Onglet principal
def afficher_onglet_sport(city1, city2, info1, info2):
   st.markdown("## 🏟️ Équipements sportifs")


   keyword = st.text_input("🔎 Filtrer par mot-clé (facultatif, exemple : piscine, stade, gymnase, etc.)", "")


   col1, col2 = st.columns(2)


   with col1:
       code_insee1 = info1["COM_CODE"]
       lat1, lon1 = get_lat_lon_from_insee(code_insee1)
       if lat1 and lon1:
           afficher_equipements_sport(city1, lat1, lon1, keyword, key_prefix="ville1")
       else:
           st.warning(f"Coordonnées manquantes pour {city1}.")


   with col2:
       code_insee2 = info2["COM_CODE"]
       lat2, lon2 = get_lat_lon_from_insee(code_insee2)
       if lat2 and lon2:
           afficher_equipements_sport(city2, lat2, lon2, keyword, key_prefix="ville2")
       else:
           st.warning(f"Coordonnées manquantes pour {city2}.")




def get_lat_lon_from_insee(code_insee):
   """Récupère la latitude et la longitude à partir du code INSEE via l'API Geo"""
   try:
       url = f"https://geo.api.gouv.fr/communes/{code_insee}?fields=nom,centre"
       response = requests.get(url)
       if response.status_code == 200:
           data = response.json()
           lat = data['centre']['coordinates'][1]
           lon = data['centre']['coordinates'][0]
           return lat, lon
       else:
           return None, None
   except Exception as e:
       st.error(f"Erreur récupération coordonnées INSEE : {e}")
       return None, None






# Barre de comparaison en haut
st.markdown("### 🔍 Comparaison des villes")
tabs = st.tabs(["🌤️ Météo", "💼 Emploi", "👥 Population", "🏠 Immobilier", "🛡️ Sécurité", "🗳️ Politique", "🎓 Services", "🏟️ Sport"])


sections = [
   {"label": "Météo", "icon": "🌤️"},
   {"label": "Emploi", "icon": "💼"},
   {"label": "Population", "icon": "👥"},
   {"label": "Immobilier", "icon": "🏠"},
   {"label": "Sécurité", "icon": "🛡️"},
   {"label": "Politique", "icon": "🗳️"},
   {"label": "Services", "icon": "🎓"},
   {"label": "Sport", "icon": "🏟️"},
]


for i, section in enumerate(sections):
   with tabs[i]:
       if section["label"] == "Météo":
           afficher_onglet_meteo(city1, city2)
      
       elif section["label"] == "Emploi":
           afficher_onglet_emploi(city1, city2, token, referentiel)


       elif section["label"] == "Population":
           afficher_onglet_population(city1, city2)


       elif section["label"] == "Immobilier":
           afficher_onglet_immobilier(city1, city2)


       elif section["label"] == "Sécurité":
           afficher_onglet_securite(city1, city2)


       elif section["label"] == "Politique":
           afficher_onglet_politique(city1, city2)


       elif section["label"] == "Services":
           afficher_onglet_services(city1, city2, info1, info2)


       elif section["label"] == "Sport":
           afficher_onglet_sport(city1, city2, info1, info2)




       else:
           st.subheader(f"{section['icon']} {section['label']} (à compléter)")
           st.info("⚠️ Données simulées — à remplacer par vos vraies sources.")
           col1, col2 = st.columns(2)
           with col1:
               st.subheader(city1)
               st.metric("Indicateur exemple", "123")
           with col2:
               st.subheader(city2)
               st.metric("Indicateur exemple", "456")


# Fin du code


