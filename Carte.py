import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import logging

# Configuration de la journalisation
logging.basicConfig(filename='geocoding_errors.log', level=logging.ERROR)

# Charger les données
data = pd.read_csv('Pharmacies_Charlotte_Cleaned.csv', delimiter=';')

# Ajouter latitude et longitude
geolocator = Nominatim(user_agent="pharmacy_locator")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_lat_lon(postal_code, city):
    try:
        location = geocode(f"{postal_code} {city}, France")
        if location:
            return location.latitude, location.longitude
        logging.error(f"Geocoding failed for: {postal_code} {city}, France")
        return None, None
    except Exception as e:
        logging.error(f"Exception occurred for {postal_code} {city}, France: {e}")
        return None, None

# Appliquer le géocodage avec journalisation des erreurs
data['Latitude'], data['Longitude'] = zip(
    *data.apply(lambda row: get_lat_lon(row['Code postal'], row['Ville']), axis=1)
)

# Filtrer les données géocodées
map_data = data.dropna(subset=['Latitude', 'Longitude'])

# Vérifier le nombre d'entrées avant et après le géocodage
print(f"Total entries: {len(data)}")
print(f"Geocoded entries: {len(map_data)}")

# Créer la carte
fig = px.scatter_mapbox(
    map_data,
    lat="Latitude",
    lon="Longitude",
    hover_name="Nom de l'entreprise",
    hover_data={"Adresse postale": True, "Ville": True, "Code postal": True},
    zoom=5,
    height=600
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Enregistrer la carte
fig.write_html('Pharmacy_Mapp.html')
