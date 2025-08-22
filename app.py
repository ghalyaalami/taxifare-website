import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import pydeck as pdk

'''
# TaxiFareModel front
'''

st.markdown('''

''')

url = 'https://taxifare.lewagon.ai/predict'




#2. Let's build a dictionary containing the parameters for our API...


st.markdown("## 🚕 Taxi Fare Prediction")

# 1) Demander les infos à l’utilisateur
d = st.date_input("📅 Pickup date")
t = st.time_input("⏰ Pickup time")

pickup_lon   = st.number_input("📍 Pickup longitude", value=-73.985428, format="%.6f")
pickup_lat   = st.number_input("📍 Pickup latitude",  value=40.748817,  format="%.6f")
dropoff_lon  = st.number_input("📍 Dropoff longitude", value=-73.985428, format="%.6f")
dropoff_lat  = st.number_input("📍 Dropoff latitude",  value=40.732610,  format="%.6f")
passengers   = st.number_input("👥 Passenger count", min_value=1, max_value=8, value=1, step=1)

# 2) Construire le dictionnaire avec les valeurs de l’utilisateur
pickup_datetime = datetime.combine(d, t).strftime("%Y-%m-%d %H:%M:%S")

params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": float(pickup_lon),
    "pickup_latitude": float(pickup_lat),
    "dropoff_longitude": float(dropoff_lon),
    "dropoff_latitude": float(dropoff_lat),
    "passenger_count": int(passengers)
}

# 3) Debug: afficher les paramètres




#3. Let's call our API using the `requests` package...
response = requests.get(url, params=params)



#4. Let's retrieve the prediction from the **JSON** returned by the API...
if response.status_code == 200 :
    st.write("The taxifare is :", response.json()["fare"])
else :
    st.error(f"❌ API call failed with status {response.status_code}")
    st.text(response.text)

## Finally, we can display the prediction to the user

# maintenant on va créer une carte avec nos points de depart et d'arrivée

df_points = pd.DataFrame([
    {"lat": float(pickup_lat),  "lon": float(pickup_lon),  "name": "pickup", "emoji": "🚶"},
    {"lat": float(dropoff_lat), "lon": float(dropoff_lon), "name": "dropoff", "emoji": "🎯"},
])






#st.subheader("🗺️ Carte - points pickup & dropoff")
#st.map(df_points, latitude="lat", longitude="lon", zoom=12)





def icon(url):
    return {"url": url, "width": 72, "height": 72, "anchorY": 72}  # ancre en bas

df_icons = pd.DataFrame([
    {
        "lat": float(pickup_lat), "lon": float(pickup_lon),
        "name": "Départ",
        "icon": icon("https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f6b6.png")  # 🚶
    },
    {
        "lat": float(dropoff_lat), "lon": float(dropoff_lon),
        "name": "Arrivée",
        "icon": icon("https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f3af.png")  # 🎯
    },
])


# 1) Light tile layer (pick ONE of these)
tile_layer = pdk.Layer(
    "TileLayer",
    data=None,
    min_zoom=0, max_zoom=19, tile_size=256,
    # OpenStreetMap standard (light)
    get_tile_data="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
)
# Or Carto Positron (also light)
# tile_layer = pdk.Layer(
#     "TileLayer", data=None, min_zoom=0, max_zoom=19, tile_size=256,
#     get_tile_data="https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
# )

# 2) Your icon layer (unchanged)
icon_layer = pdk.Layer(
    "IconLayer",
    data=df_icons,
    get_icon="icon",
    get_position='[lon, lat]',
    size_scale=8,
    get_size=4,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=df_icons["lat"].mean(),
    longitude=df_icons["lon"].mean(),
    zoom=12
)

# 3) IMPORTANT: remove Mapbox basemap by setting map_style=None
deck = pdk.Deck(
    initial_view_state=view_state,
    layers=[tile_layer, icon_layer],
    map_style=None,                       # <- prevents dark Mapbox style
    # parameters={"clearColor": [1, 1, 1, 1]},  # optional: white background while tiles load
    tooltip={"text": "{name}\n[{lat}, {lon}]"},
)

st.pydeck_chart(deck)
