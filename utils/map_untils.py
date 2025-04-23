import folium
from streamlit_folium import st_folium

def show_map(lat, lon, city_name):
    m = folium.Map(location=[lat, lon], zoom_start=11)
    folium.Marker([lat, lon], popup=city_name).add_to(m)
    st_folium(m, width=500, height=350)