# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
df = pd.read_csv('merged_data.csv')
geoloc_df = pd.read_csv('archive/olist_geolocation_dataset.csv')

# %%
delay = (pd.to_datetime(df["order_estimated_delivery_date"]) - pd.to_datetime(df["order_delivered_customer_date"])).dt.days

# %%
df["delay"] = delay

# %%
geo_aggregated = geoloc_df.groupby('geolocation_zip_code_prefix').agg({
    'geolocation_lat': 'mean',
    'geolocation_lng': 'mean'
}).reset_index()

# %%
geo_aggregated

# %%
df = df.merge(geo_aggregated, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')

# %%
df

# %%
df.groupby("customer_city")["delay"].mean().sort_values(ascending=False)[:10].plot(kind="bar")
plt.xticks(rotation=45)

# %%
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point

data = df.copy()
# Filtrage des données pour l'Amérique du Sud
filtered_data = data[
    (data['geolocation_lat'] > -60) & (data['geolocation_lat'] < 15) &  # Latitudes
    (data['geolocation_lng'] > -80) & (data['geolocation_lng'] < -30)  # Longitudes
]

# Charger les données de carte pour l'Amérique du Sud
world = gpd.read_file('geo_panda_maps/ne_110m_admin_0_countries.shp')

# Tracer la carte
fig, ax = plt.subplots(figsize=(12, 8))
world[world['CONTINENT'] == 'South America'].plot(ax=ax, color='lightgrey', edgecolor='black')

# Ajouter une visualisation avec Seaborn
sns.scatterplot(
    x='geolocation_lng', y='geolocation_lat', size='delay', sizes=(10, 200),
    hue='delay', palette="coolwarm", data=filtered_data, ax=ax, alpha=0.8,
    legend=False  # On va utiliser un colorbar personnalisé
)

# Ajouter un colorbar avec des limites spécifiques
sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(vmin=0, vmax=15))  # Plage de 0 à 15 jours
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("Retard moyen (jours)", fontsize=12)

# Titres et légendes
ax.set_title("Carte des retards moyens par localisation", fontsize=16)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.show()


