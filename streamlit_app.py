import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Set the title and favicon for the browser tab.
st.set_page_config(page_title="GDP and Inventory Dashboard", page_icon=":earth_americas:")

# -----------------------------------------------------------------------------
# Step 1: Complex GDP Dashboard

@st.cache_data
def get_gdp_data():
    """Fetch and prepare GDP data."""
    # Use a relative path to the CSV file containing GDP data
    gdp_file = Path(__file__).parent / "gdp_data.csv"
    raw_gdp_df = pd.read_csv(gdp_file)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # Pivot the data to have 'Year' and 'GDP' columns
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

# Load and display the GDP data
gdp_df = get_gdp_data()

st.title(":earth_americas: GDP Dashboard")
st.write("Browse GDP data from the World Bank Open Data website.")

# Select year range with a slider
min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

# Select countries to view
countries = gdp_df['Country Code'].unique()

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

# Filter GDP data based on selections
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

# Display the GDP line chart
st.header('GDP Over Time')
st.line_chart(filtered_gdp_df, x='Year', y='GDP', color='Country Code')

# Display summary of GDP for the selected time period
first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}')

# Display GDP metrics for selected countries
cols = st.columns(4)
for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]
    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1e9
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1e9
        growth = f'{last_gdp / first_gdp:,.2f}x' if first_gdp != 0 else 'n/a'
        st.metric(label=f'{country} GDP', value=f'{last_gdp:,.0f}B', delta=growth)

# -----------------------------------------------------------------------------
# Step 2: User Login for Inventory Data

# Get user credentials from Streamlit secrets
def get_user_credentials():
    """Extract credentials from Streamlit secrets."""
    credentials = {}
    for user_key in st.secrets["credentials"]:
        user_info = st.secrets["credentials"][user_key]
        credentials[user_info["username"]] = user_info["password"]
    return credentials

user_credentials = get_user_credentials()

# Login form
st.subheader("Login to Access Inventory Data")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Verify login and load inventory data
if st.button("Login"):
    if username in user_credentials and password == user_credentials[username]:
        st.success(f"Welcome {username}!")

        # Load inventory data based on the username (e.g., user1.csv, user2.csv)
        inventory_file = Path(__file__).parent / f"{username}.csv"
        try:
            inventory_df = pd.read_csv(inventory_file)

            # Display the inventory table
            st.subheader(f"Inventory Data for {username}")
            st.dataframe(inventory_df)

            # Display inventory charts
            st.subheader("Units Left")
            need_to_reorder = inventory_df[inventory_df["units_left"] < inventory_df["reorder_point"]].loc[:, "item_name"]
            if not need_to_reorder.empty:
                st.error(f"Items to reorder: {', '.join(need_to_reorder)}")

            st.altair_chart(
                alt.Chart(inventory_df)
                .mark_bar()
                .encode(x="units_left", y="item_name"),
                use_container_width=True,
            )

            st.subheader("Best Sellers")
            st.altair_chart(
                alt.Chart(inventory_df)
                .mark_bar(orient="horizontal")
                .encode(x="units_sold", y=alt.Y("item_name").sort("-x")),
                use_container_width=True,
            )
        except FileNotFoundError:
            st.error(f"CSV file for {username} not found.")
    else:
        st.error("Incorrect username or password. Please try again.")
