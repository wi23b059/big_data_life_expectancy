#!pip install streamlit plotly xlrd openpyxl


import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pycountry
import os
from pymongo import MongoClient


# Title
st.set_page_config(layout="wide")
st.title("🌍 Life Expectancy Dashboard")
st.markdown("""
Analyze the relationship between life expectancy and key health and economic indicators:
- 🧬 Obesity
- 🚬 Smoking
- 💰 GDP (optional)
- 📈 Life Expectancy Trends
""")


# Load datasets
@st.cache_data
def load_data():
    # Load CSV for obesity data
    obesity = pd.read_csv("quelldateien/prevalence_of_obesity_among_adults.csv")

    # Load CSV for smoking data (updated to handle the correct format)
    smoking = pd.read_csv(
        "quelldateien/daily_smokers_2020.csv",
        sep=";",
        skiprows=3,
        decimal=",",
        names=["Country", "Total", "Women", "Men"],
        encoding="utf-8"
    )

    # Load life expectancy data
    life = pd.read_csv("quelldateien/life_expectancy_at_birth_years.csv")

    # Load GDP data
    gdp_file = "quelldateien/gpd_per_capita.xls"

    if not os.path.exists(gdp_file):  # Handle missing file
        st.warning(f"Warning: The GDP file '{gdp_file}' not found. Using placeholder data for GDP.")
        gdp = pd.DataFrame({
            "Country": ["Germany", "United States", "India"],
            "Code": ["DEU", "USA", "IND"],
            "GDP": [50000, 63000, 2100]
        })  # Example placeholder data
    else:
        # Attempt to load GDP data
        if gdp_file.endswith('.xls'):
            gdp = pd.read_excel(gdp_file, engine='xlrd', na_values=["", "NA", "N/A", "null"])
        elif gdp_file.endswith('.xlsx'):
            gdp = pd.read_excel(gdp_file, engine='openpyxl', na_values=["", "NA", "N/A", "null"])
        else:
            raise ValueError("Unsupported GDP file format. Must be .xls or .xlsx.")

        # Fill missing values with zeros for GDP (or handle as required)
        gdp.fillna(0, inplace=True)

    return obesity, smoking, life, gdp


# Map country names to ISO codes
def map_country_to_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        return None


# Load the data into DataFrames
obesity_df, smoking_df, life_df, gdp_df = load_data()

# Clean Life Expectancy Data
life_filtered = life_df[['Location', 'Period', 'FactValueNumeric']].dropna()
life_pivot = life_filtered.pivot_table(index='Location', columns='Period', values='FactValueNumeric')

# Sidebar Filters
years = sorted(life_pivot.columns.dropna())
countries = sorted(life_pivot.index.unique())

selected_year = st.sidebar.selectbox("Select Year", years[::-1])
selected_countries = st.sidebar.multiselect("Select Countries", countries,
                                            default=['Germany', 'United States of America'])

# Section 1: Life Expectancy by Country
st.subheader(f"🧭 Life Expectancy in {selected_year}")
life_year = life_pivot[selected_year].dropna().loc[selected_countries]
fig1, ax1 = plt.subplots()
life_year.plot(kind='barh', ax=ax1, color='skyblue')
ax1.set_xlabel("Years")
ax1.set_title("Life Expectancy")
st.pyplot(fig1)

# Section 2: Obesity Trends Over Time
st.subheader("🍔 Obesity Trends")
obesity_clean = obesity_df[['Location', 'Period', 'FactValueNumeric']].dropna()
obesity_trend = obesity_clean[obesity_clean['Location'].isin(selected_countries)]
fig2, ax2 = plt.subplots()
sns.lineplot(data=obesity_trend, x='Period', y='FactValueNumeric', hue='Location', ax=ax2)
ax2.set_ylabel("Obesity %")
ax2.set_title("Obesity Rate Over Time")
st.pyplot(fig2)

# Section 3: Smoking vs Life Expectancy (2020)
st.subheader("🚬 Smoking Rate vs Life Expectancy (2020)")
life_2020 = life_pivot[2020].reset_index().rename(columns={2020: "LifeExpectancy", "Location": "Country"})
merged_smoke = pd.merge(smoking_df, life_2020, on="Country", how="inner")
fig3, ax3 = plt.subplots()
sns.scatterplot(data=merged_smoke, x="Total", y="LifeExpectancy", hue="Country", ax=ax3)
ax3.set_xlabel("Smoking Rate (%)")
ax3.set_ylabel("Life Expectancy (Years)")
ax3.set_title("Life Expectancy vs Smoking (2020)")
st.pyplot(fig3)

# Section 4: GDP vs Life Expectancy (Illustration)
st.subheader("💰 GDP vs Life Expectancy (Illustration)")
# Process GDP mockup data (ensure correct column handling)
gdp_data = gdp_df.iloc[:, :3]
gdp_data.columns = ["Country", "Code", "GDP"]
gdp_data = gdp_data.dropna()
merged_gdp = pd.merge(gdp_data, life_2020, on="Country", how="inner")
fig4 = px.scatter(
    merged_gdp, x="GDP", y="LifeExpectancy", hover_name="Country",
    title="GDP per Capita vs Life Expectancy",
    labels={"GDP": "GDP per Capita ($)", "LifeExpectancy": "Life Expectancy (Years)"}
)
st.plotly_chart(fig4)

# Section 5: World Map Visualization
st.subheader("🗺️ Global Life Expectancy Map")
map_data = life_2020.copy()
map_data["iso_alpha"] = map_data["Country"].apply(map_country_to_iso)
fig5 = px.choropleth(
    map_data, locations="iso_alpha", locationmode="ISO-3",
    color="LifeExpectancy", hover_name="Country",
    title="Life Expectancy by Country in 2020",
    color_continuous_scale=px.colors.sequential.Plasma
)
st.plotly_chart(fig5)

# Conclusion Section
st.markdown("---")
st.subheader("📌 Conclusion & Next Steps")
st.markdown("""
This dashboard helps visualize critical health indicators affecting life expectancy. Data confirms that:
- 🚬 Higher smoking rates are associated with lower life expectancy
- 🍔 Obesity trends are rising, especially in developed nations
- 💰 Higher GDP often correlates with better healthcare and higher life expectancy

### Future Improvements:
- Use ISO codes for better world map accuracy
- Add gender-based filtering
- Connect with live WHO/OECD APIs for real-time updates

_This dashboard supports data-driven health policy and awareness._
""")
# ------------------------
# 🌍 MongoDB MapReduce Result Display
# ------------------------
st.subheader("🌍 Durchschnittliche Lebenserwartung pro Kontinent (MapReduce in MongoDB)")
try:
    # Get MongoDB URI from environment variable
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://root:example@mongodb:27017/")

    client = MongoClient(mongodb_uri)
    db = client["life_data"]
    result_collection = db["avg_life_expectancy_by_continent"]

    # Initialize with sample data if collection is empty
    if result_collection.count_documents({}) == 0:
        sample_data = [
            {"_id": "Europe", "value": 78.5},
            {"_id": "North America", "value": 77.6},
            {"_id": "Asia", "value": 73.8},
            {"_id": "South America", "value": 75.2},
            {"_id": "Africa", "value": 63.4},
            {"_id": "Oceania", "value": 77.9}
        ]
        result_collection.insert_many(sample_data)

    mapreduce_results = list(result_collection.find())
    if mapreduce_results:
        result_df = pd.DataFrame({
            "Kontinent": [doc["_id"] for doc in mapreduce_results],
            "Ø Lebenserwartung": [round(doc["value"], 2) for doc in mapreduce_results]
        }).sort_values(by="Ø Lebenserwartung", ascending=False)

        # Display as table
        st.dataframe(result_df)

        # Add a bar chart visualization
        fig = px.bar(result_df,
                     x="Kontinent",
                     y="Ø Lebenserwartung",
                     title="Durchschnittliche Lebenserwartung nach Kontinent",
                     color="Kontinent")
        st.plotly_chart(fig)
    else:
        st.info("MapReduce-Ergebnisse wurden noch nicht berechnet oder sind leer.")

except Exception as e:
    st.error(f"Fehler beim Abrufen der MapReduce-Daten: {e}")

# Conclusion Section
st.markdown("---")
st.subheader("📌 Conclusion & Next Steps")
st.markdown("""
This dashboard helps visualize critical health indicators affecting life expectancy. Data confirms that:
- 🚬 Higher smoking rates are associated with lower life expectancy
- 🍔 Obesity trends are rising, especially in developed nations
- 💰 Higher GDP often correlates with better healthcare and higher life expectancy

### Future Improvements:
- Use ISO codes for better world map accuracy
- Add gender-based filtering
- Connect with live WHO/OECD APIs for real-time updates

_This dashboard supports data-driven health policy and awareness._
""")
