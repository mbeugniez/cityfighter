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



def afficher_onglet_emploi(ville1, ville2):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); margin-top: 1rem;">
                <h3 style="color: #e2001a; text-align: center;">💼 Emploi à {ville1}</h3>
                <ul style="font-size: 16px; line-height: 1.6;">
                    <li><strong>Actifs :</strong> 10 500</li>
                    <li><strong>Actifs occupés :</strong> 9 200</li>
                    <li><strong>Chômeurs :</strong> 1 300</li>
                    <li><strong>Taux d'activité :</strong> 75 %</li>
                    <li><strong>Taux d'emploi :</strong> 66 %</li>
                    <li><strong>Taux de chômage :</strong> 12 %</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); margin-top: 1rem;">
                <h3 style="color: #e2001a; text-align: center;">💼 Emploi à {ville2}</h3>
                <ul style="font-size: 16px; line-height: 1.6;">
                    <li><strong>Actifs :</strong> 8 700</li>
                    <li><strong>Actifs occupés :</strong> 7 500</li>
                    <li><strong>Chômeurs :</strong> 1 200</li>
                    <li><strong>Taux d'activité :</strong> 71 %</li>
                    <li><strong>Taux d'emploi :</strong> 63 %</li>
                    <li><strong>Taux de chômage :</strong> 14 %</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)


def afficher_onglet_population(city1, city2):
    st.markdown("## 👥 Population (exemple fictif)")
    st.markdown("Indicateurs inspirés de l'INSEE – données fictives à adapter.")

    col1, col2 = st.columns(2)

    for col, city, color in zip([col1, col2], [city1, city2], ['#1f77b4', '#ff7f0e']):
        with col:
            st.markdown(f"""
            <div style="background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 0 12px rgba(0,0,0,0.08);">
                <h3 style="text-align:center; color:#c8102e;">Population à {city}</h3>
                <div style="display:flex; justify-content:space-around; flex-wrap:wrap; text-align:center; font-size:16px; margin-top:20px;">
                    <div><strong style="color:#c8102e; font-size:24px;">{np.random.randint(19000, 26000):,}</strong><br>habitants</div>
                    <div><strong style="color:green; font-size:24px;">+{round(np.random.uniform(0.5, 2.5),2)}%</strong><br>entre 2016-2022</div>
                    <div><strong style="color:#c8102e; font-size:24px;">{np.random.randint(400, 1300)}</strong><br>hab/km²</div>
                    <div><strong style="color:#c8102e; font-size:24px;">{np.random.randint(35, 55)} ans</strong><br>âge médian</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<h4 style='color:#c8102e; margin-top:30px;'>Évolution de la population</h4>", unsafe_allow_html=True)
            years = np.arange(2012, 2023)
            pop = np.random.randint(15000, 25000, size=len(years))
            fig, ax = plt.subplots()
            ax.plot(years, pop, marker='o', color=color)
            ax.set_ylabel("Habitants")
            ax.set_xlabel("Année")
            ax.grid(True)
            st.pyplot(fig)

            st.markdown("<h4 style='color:#c8102e;'>Répartition par âge</h4>", unsafe_allow_html=True)
            ages = ["0-14", "15-29", "30-44", "45-59", "60-74", "75+"]
            age_pct = np.random.randint(5, 25, size=len(ages))
            for age, pct in zip(ages, age_pct):
                st.markdown(f"""
                    <div style="margin:8px 0;">
                        <div style="width:{pct}%; background:#f5425d; height:16px; border-radius:4px; display:inline-block;"></div>
                        <span style="margin-left:10px;">{pct}% {age} ans</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<h4 style='color:#c8102e;'>Niveau de diplôme</h4>", unsafe_allow_html=True)
            diplomes = ["Sans diplôme", "CAP/BEP", "Bac", "Bac+2/3", "Bac+5 et plus"]
            pct_diplomes = np.random.randint(5, 30, size=len(diplomes))
            for d, p in zip(diplomes, pct_diplomes):
                st.markdown(f"""
                    <div style="margin:8px 0;">
                        <div style="width:{p}%; background:#1f77b4; height:16px; border-radius:4px; display:inline-block;"></div>
                        <span style="margin-left:10px;">{p}% {d}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


def afficher_onglet_immobilier(city1, city2):
    st.markdown("## 🏠 Immobilier (exemple fictif)")
    st.markdown("Analyse immobilière basée sur des données fictives inspirées de l'INSEE.")

    col1, col2 = st.columns(2)

    for col, city in zip([col1, col2], [city1, city2]):
        with col:
            st.markdown(f"""
                <div style="background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h3 style="color: #c8102e; text-align: center;">Immobilier à {city}</h3>
                    <p style="text-align: justify;">Les habitants de {city} vivent majoritairement dans une maison et sont très souvent propriétaires de leur logement. L’habitat est ancien, avec une majorité de logements datant d’avant 1970. Les surfaces sont grandes et de nombreux logements comptent plus de 4 pièces.</p>
                    <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
                        <div style="text-align:center;">
                            🏢<br><strong>-</strong><br><small>Prix m² appart</small>
                        </div>
                        <div style="text-align:center;">
                            🏠<br><strong>-</strong><br><small>Prix m² maison</small>
                        </div>
                    </div>
            """, unsafe_allow_html=True)

            # 🥧 Camembert - Type d’habitat
            st.markdown("### 🏘️ Type d’habitat", unsafe_allow_html=True)
            labels = ['Maisons', 'Appartements']
            sizes = [100, 0]
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct='%1.0f %%', startangle=90, colors=['#f5425d', '#ddd'])
            ax1.axis('equal')
            st.pyplot(fig1)

            # 🥧 Camembert - Statut d'occupation
            st.markdown("### 👤 Habitants", unsafe_allow_html=True)
            labels2 = ['Propriétaires', 'Locataires']
            sizes2 = [91.8, 8.2]
            fig2, ax2 = plt.subplots()
            ax2.pie(sizes2, labels=labels2, autopct='%1.1f %%', startangle=90, colors=['#f5425d', '#1f77b4'])
            ax2.axis('equal')
            st.pyplot(fig2)

            # Barres - Usage des habitations
            st.markdown("### 🏡 Usage des habitations", unsafe_allow_html=True)
            usages = ["Logements vacants", "Résidences principales", "Résidences secondaires"]
            usage_pct = [10.4, 80.5, 9.1]
            for label, val in zip(usages, usage_pct):
                st.markdown(f"""
                    <div style="margin:6px 0;">
                        <div style="width:{val}%; background:#f5425d; height:14px; border-radius:4px; display:inline-block;"></div>
                        <span style="margin-left:10px;">{val:.1f}% {label}</span>
                    </div>
                """, unsafe_allow_html=True)

            # Barres - Nombre de pièces
            st.markdown("### 🛏️ Nombre de pièces", unsafe_allow_html=True)
            nb_pieces = ["1 pièce", "2 pièces", "3 pièces", "4 pièces", "5 pièces et plus"]
            pieces_pct = [3.3, 4.9, 8.2, 26.2, 57.4]
            for label, val in zip(nb_pieces, pieces_pct):
                st.markdown(f"""
                    <div style="margin:6px 0;">
                        <div style="width:{val}%; background:#f5425d; height:14px; border-radius:4px; display:inline-block;"></div>
                        <span style="margin-left:10px;">{val:.1f}% {label}</span>
                    </div>
                """, unsafe_allow_html=True)

            # Bas
            st.markdown("<p style='font-size:12px; color:gray;'>Source : Données fictives INSEE / DVF</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

def afficher_onglet_securite(city1, city2):
    st.markdown("## 🛡️ Sécurité")
    st.markdown("Comparaison du taux de criminalité pour 100 000 habitants. Données fictives à remplacer.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.08);">
            <h4 style="color: #c8102e;">{city1}</h4>
            <p><strong style="font-size: 24px; color: #d90429;">3 159</strong> crimes et délits pour 100 000 habitants.</p>
            <p><strong>Moyenne nationale :</strong> 5 258</p>
            <p>Cette commune dépend de la zone CGD fictive X regroupant 180 communes.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.08);">
            <h4 style="color: #c8102e;">{city2}</h4>
            <p><strong style="font-size: 24px; color: #d90429;">2 781</strong> crimes et délits pour 100 000 habitants.</p>
            <p><strong>Moyenne nationale :</strong> 5 258</p>
            <p>Cette commune dépend de la zone CGD fictive Y regroupant 170 communes.</p>
        </div>
        """, unsafe_allow_html=True)

    # Tableau comparatif
    st.markdown("### 📊 Détails par type d'infraction")
    data = {
        "Infraction": [
            "Cambriolages",
            "Vols automobiles",
            "Vols de particulier",
            "Violences physiques",
            "Violences sexuelles"
        ],
        city1: [407, 493, 322, 387, 67],
        city2: [390, 470, 280, 310, 72],
        "National": [518, 707, 1019, 655, 76]
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)



def afficher_onglet_politique(city1, city2):
    st.markdown("## 🗳️ Politique")
    st.markdown("Résultats fictifs des dernières élections présidentielles comparées.")

    elections = [
        {"année": "2022", "candidat1": "Marine LE PEN", "score1": 50, "candidat2": "Emmanuel MACRON", "score2": 50},
        {"année": "2017", "candidat1": "Emmanuel MACRON", "score1": 56, "candidat2": "Marine LE PEN", "score2": 44},
        {"année": "2012", "candidat1": "Nicolas SARKOZY", "score1": 63.89, "candidat2": "François HOLLANDE", "score2": 36.11},
        {"année": "2007", "candidat1": "Nicolas SARKOZY", "score1": 63.93, "candidat2": "Ségolène ROYAL", "score2": 36.07},
    ]

    for e in elections:
        col1, col2 = st.columns(2)

        for col, city, score, candidat_gagnant, candidat_perdant, score_perdant in zip(
            [col1, col2],
            [city1, city2],
            [e["score1"], e["score2"]],
            [e["candidat1"], e["candidat2"]],
            [e["candidat2"], e["candidat1"]],
            [e["score2"], e["score1"]],
        ):
            with col:
                st.markdown(f"""
                    <div style="background-color:white; padding:25px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.07); margin-bottom:1.5rem;">
                        <h4 style="text-align:center; color:#2c3e50;">{city} – {e['année']}</h4>
                        <div style="text-align:center;">
                            <div style="margin:auto; width:120px; height:120px; border-radius:50%; border:10px solid #ffcc00; display:flex; align-items:center; justify-content:center; font-size:28px; font-weight:bold;">
                                {score}%
                            </div>
                            <div style="font-size:18px; margin-top:10px; color:#c8102e;"><strong>{candidat_gagnant}</strong></div>
                            <div style="font-size:14px; color:#333;">{score_perdant} % {candidat_perdant}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:13px; text-align:center; margin-top:10px; color:#777;'>Source : Ministère de l’Intérieur (simulation)</p>", unsafe_allow_html=True)



def afficher_onglet_services(city1, city2):
    st.markdown("## 🏛️ Services publics et commodités")
    st.markdown("Vue comparative des services disponibles autour des deux villes sélectionnées.")

    services = {
        "🩺 Services de santé": {
            "Médecin": ["Songeons (5,1 km)", "Achères (2,1 km)"],
            "Dentiste": ["Marseille-en-Beauvaisis (9,3 km)", "Poissy (3,5 km)"],
            "Pharmacie": ["Songeons (5,1 km)", "Achères (2 km)"],
            "Urgences": ["Beauvais (23,6 km)", "Cergy-Pontoise (14,8 km)"]
        },
        "🎓 Éducation": {
            "Crèche": ["Hécourt (9,5 km)", "Achères (1,5 km)"],
            "École maternelle": ["Hautbos (4,8 km)", "Achères (1 km)"],
            "Collège": ["Marseille-en-Beauvaisis (9 km)", "Andrésy (3 km)"],
            "Lycée": ["Forges-les-Eaux (21,5 km)", "Conflans (5 km)"]
        },
        "🛒 Commerces": {
            "Hypermarché": ["Ferrières-en-Bray (14,4 km)", "Carrefour Chambourcy (9 km)"],
            "Supermarché": ["Feuquières (6,2 km)", "Achères (2 km)"],
            "Boulangerie": ["Morvillers (3,3 km)", "Achères (1 km)"],
            "Station-service": ["Songeons (5,2 km)", "BP Achères (1.5 km)"]
        },
        "🎭 Transports & Loisirs": {
            "Hôtel": ["Grandvilliers (11,6 km)", "Ibis Poissy (7 km)"],
            "Cinéma": ["Gournay-en-Bray (14,5 km)", "Cinéma Cergy (10 km)"],
            "Bibliothèque": ["Songeons (5,3 km)", "Achères (1 km)"],
            "Gare SNCF": ["Formerie (10,3 km)", "Achères-Ville (0.5 km)"]
        }
    }

    for section, entries in services.items():
        st.markdown(f"<h4 style='color:#c8102e; margin-top: 40px;'>{section}</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        for col, ville, side in zip([col1, col2], [city1, city2], [0, 1]):
            with col:
                content = f"""
                    <div style='
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                        margin-bottom: 20px;
                    '>
                        <h5 style='color: #2c3e50; font-size: 18px; margin-bottom: 15px;'>{ville}</h5>
                """

                for label, val in entries.items():
                    content += f"<p><strong>{label}</strong> : {val[side]}</p>"

                content += "</div>"
                st.markdown(content, unsafe_allow_html=True)

    st.markdown("<p style='font-size:12px; text-align:center; margin-top:30px; color:#888;'>Source : Base permanente des équipements (BPE), INSEE – Données fictives</p>", unsafe_allow_html=True)



# Barre de comparaison en haut
st.markdown("### 🔍 Comparaison des villes")
tabs = st.tabs(["🌤️ Météo", "💼 Emploi", "👥 Population", "🏠 Immobilier", "🛡️ Sécurité", "🗳️ Politique", "🎓 Services"])

sections = [
    {"label": "Météo", "icon": "🌤️"},
    {"label": "Emploi", "icon": "💼"},
    {"label": "Population", "icon": "👥"},
    {"label": "Immobilier", "icon": "🏠"},
    {"label": "Sécurité", "icon": "🛡️"},
    {"label": "Politique", "icon": "🗳️"},
    {"label": "Services", "icon": "🎓"},
]

for i, section in enumerate(sections):
    with tabs[i]:
        if section["label"] == "Météo":
            afficher_onglet_meteo(city1, city2)
        
        elif section["label"] == "Emploi":
            afficher_onglet_emploi(city1, city2)

        elif section["label"] == "Population":
            afficher_onglet_population(city1, city2)

        elif section["label"] == "Immobilier":
            afficher_onglet_immobilier(city1, city2)

        elif section["label"] == "Sécurité":
            afficher_onglet_securite(city1, city2)

        elif section["label"] == "Politique":
            afficher_onglet_politique(city1, city2)

        elif section["label"] == "Services":
            afficher_onglet_services(city1, city2)

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