import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
sns.set(style="whitegrid")

st.title("Mini Projet Streamlit")
st.subheader("Bienvenue sur mon tableau de bord de ventes des étudiants!")
st.write("-----")


data=pd.read_csv('donnees_ventes_etudiants_.csv', index_col=False, dtype='unicode')

# """
# 2 - Créer une nouvelle colonne dans votre table qui sera
# nommé State Complet : et remplacer les noms abrégés de State
# par leur vrai noms
# """
state_mapping = pd.read_csv('states.csv')
state_mapping = state_mapping.set_index('Abbreviation')['State'].to_dict()

data['State Complet'] = data['State'].map(state_mapping)

#st.write(data)

st.sidebar.header("Effectuer des filtre:")
region_choose = st.sidebar.multiselect(
    "Selectionner une Région:",
    options=data["Region"].unique(),
    default=data["Region"].unique()[0]
)

state_choose = st.sidebar.multiselect(
    "electionner un état:",
    options=data[data['Region'].isin(region_choose)]['State Complet'].unique() if region_choose else data["State Complet"].unique(),
    #default=data["State Complet"].unique()[8],
)

country_choose = st.sidebar.multiselect(
    "electionner une comté:",
    options = data[data['State Complet'].isin(state_choose)]['County'].unique() if state_choose else data["County"].unique(),
    #options=data["County"].unique(),
    #default=data["County"].unique()[0],
)

city_choose = st.sidebar.multiselect(
    "electionner une ville:",
    options=data[data['County'].isin(country_choose)]['City'].unique() if country_choose else data["City"].unique(),
    #default=data["City"].unique()[0]
)

left_column, right_column = st.columns(2)
order_date = pd.to_datetime(data['order_date'], format="%Y-%m-%d")

with left_column:
    st.subheader('Début')
    start_date = st.date_input("Date de début", min_value=order_date.min(), max_value=order_date.max(), value=order_date.min())

with right_column:
    st.subheader('Fin')
    end_date = st.date_input("Date de fin", min_value=order_date.min(), max_value=order_date.max(), value=order_date.max())

selected_statuses = st.sidebar.multiselect(
    'Statut de la commande',
     options= data['status'].unique(),
     default=data['status'].unique()[0]
    )
start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
end_date = pd.to_datetime(end_date, format="%Y-%m-%d")

# Filter DataFrame 
#data = data.head(100)
filtered_data = data[(order_date >= start_date) & (order_date <= end_date)] 
filtered_data['total'] = pd.to_numeric(filtered_data['total'], errors='coerce')

region_filter = filtered_data['Region'].isin(region_choose) if len(region_choose) != 0 else filtered_data["Region"].unique()
state_filter = filtered_data['State Complet'].isin(state_choose) if len(state_choose) != 0 else filtered_data["State Complet"].unique
country_filter = filtered_data['County'].isin(country_choose) if len(country_choose) != 0 else filtered_data["County"].unique
city_filter = filtered_data['City'].isin(city_choose) if len(city_choose) != 0 else filtered_data["City"].unique
filter_status = filtered_data['status'].isin(selected_statuses) if len(selected_statuses) != 0 else filtered_data["status"].unique()

filtered_data = filtered_data[filter_status & region_filter]


st.write(filtered_data.shape)
total_vente = round(filtered_data['total'].sum(), 2)

distinct_clients = filtered_data['cust_id'].nunique()

total_commandes = filtered_data['order_id'].nunique()



# Affichage des KPI
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader(f"Total vente: {total_vente}")
with middle_column:
    st.subheader(f"Clients distincts : {distinct_clients}")
with right_column:
    st.subheader(f"Total commande : {total_commandes}")
st.write("-----")
left_column, right_column = st.columns(2)
with left_column:
    # Diagramme en barre pour le nombre total de vente suivant la catégorie
    if not filtered_data.empty:

        fig_bar = plt.figure(figsize=(8, 5))
        sns.barplot(x='category', y='total', data=filtered_data, estimator=sum, ci=None)


        plt.title('Nombre total de vente par catégorie')
        plt.xticks(rotation=60, ha='center')
        st.pyplot(fig_bar)
    else:
        st.write("Pas de données disponibles pour créer le diagramme en barre")

with right_column:

    # Diagramme circulaire pour le pourcentage du nombre total de vente suivant la région
    fig_pie, ax = plt.subplots()
    filtered_data.groupby('Region')['total'].sum().plot.pie(autopct='%1.1f%%', startangle=90, ax=ax)
    plt.title('Pourcentage du nombre total de vente par région')
    st.pyplot(fig_pie)
st.write("-----")
left_column, right_column = st.columns(2)
with left_column:
    # Diagramme en barre pour le TOP 10 des meilleurs clients
    top_clients = filtered_data.groupby('full_name')['total'].sum().sort_values(ascending=False).head(10)
    fig_top_clients = plt.figure(figsize=(10, 6))
    sns.barplot(x=top_clients.index, y=top_clients.values)
    plt.title('TOP 10 des meilleurs clients')
    plt.xticks(rotation=45, ha='center')
    st.pyplot(fig_top_clients)
with left_column:
    st.write()
st.write("-----")
left_column, right_column = st.columns(2)
with left_column:
   # Histogramme pour la répartition de l'âge des clients
  
   fig, ax=plt.subplots()
   st.write(sns.distplot(filtered_data['age']))
   plt.title("Histogramme pour la répartition de l'âge des clients")
   st.pyplot(fig)
with right_column:
    # Diagramme en barres pour le nombre d'hommes et de femmes
    fig, ax=plt.subplots()
    gender_counts = filtered_data['Gender'].value_counts()
    total_customers = len(filtered_data)
    percentage_male = (gender_counts.get('M', 0) / total_customers) * 100
    percentage_female = (gender_counts.get('F', 0) / total_customers) * 100
    fig, ax = plt.subplots()
    ax.bar(['M', 'F'], [percentage_male, percentage_female], color=['blue', 'pink'])
    ax.set_ylabel('Pourcentage')
    ax.set_title('Répartition par genre')
    st.pyplot(fig)
    #st.bar_chart(gender_counts)
left_column, right_column = st.columns(2)
st.write("-----")
with left_column:
    # Group by month-year and calculate total sales
    # month_uniques = filtered_data['month'].unique(),
    # st.write(month_uniques)
    # Convert 'Date' column to datetime
    filtered_data['order_date'] = pd.to_datetime(filtered_data['order_date'])


    filtered_data['Month_Year'] = filtered_data['order_date'].dt.to_period('M')
    monthly_sales = filtered_data.groupby('Month_Year')['total'].sum()
  
    fig, ax = plt.subplots()
    monthly_sales.plot(kind='line', marker='o', ax=ax)

    ax.set_ylabel('Ventes totales')
    ax.set_title('Ventes totales mensuelles')

    plt.xticks(rotation=45, ha='center')
    st.pyplot(fig)

with right_column:
    # BONUS
    def get_coordinates(country_code):
        url = f"https://www.coordonnees-gps.fr/carte/pays/{country_code}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    
    # Recherche des éléments avec l'attribut 'id' égal à 'lat' et 'lon'
        latitude_element = soup.find('input', {'id': 'lat'})
        longitude_element = soup.find('input', {'id': 'lon'})
    
    # Vérification si les éléments existent avant d'extraire les valeurs
        if latitude_element and longitude_element:
            latitude = float(latitude_element.get('value'))
            longitude = float(longitude_element.get('value'))
            return latitude, longitude
        else:
        # Gestion si les éléments ne sont pas trouvés
            return None, None


    us_latitude, us_longitude = get_coordinates('US')

   
    filtered_data['Latitude'] = us_latitude
    filtered_data['Longitude'] = us_longitude
    #st.write(filtered_data.head())

    # Streamlit
    #st.title("Ventes totales par État avec carte")

    # Plot the map using plotly
    fig = px.scatter_geo(
    filtered_data,
    lat='Latitude',
    lon='Longitude',
    size='total',
    text='State',
    projection='natural earth',
    title='Total Sales by State',
    )
    fig.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white")

    #st.plotly_chart(fig)





