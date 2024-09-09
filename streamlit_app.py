import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:',  # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Function to verify the credentials from st.secrets
def verify_credentials(input_username, input_password):
    stored_username = st.secrets["credentials"]["username"]
    stored_password = st.secrets["credentials"]["password"]
    return input_username == stored_username and input_password == stored_password

# Password Protection UI
def login():
    st.title("Login to Access the GDP Dashboard")

    # Input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # When the login button is pressed, verify credentials
    if st.button("Login"):
        if verify_credentials(username, password):
            st.success("Login successful!")
            return True
        else:
            st.error("Incorrect username or password. Please try again.")
            return False

# -----------------------------------------------------------------------------
# GDP Data and Dashboard Logic

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file and cache it."""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

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

# -----------------------------------------------------------------------------
# Main app content (shown only after login)
def main_app():
    gdp_df = get_gdp_data()

    # Set the title that appears at the top of the page.
    '''
    # :earth_americas: GDP dashboard

    Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website.
    '''

    min_value = gdp_df['Year'].min()
    max_value = gdp_df['Year'].max()

    from_year, to_year = st.slider(
        'Which years are you interested in?',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])

    countries = gdp_df['Country Code'].unique()

    if not len(countries):
        st.warning("Select at least one country")

    selected_countries = st.multiselect(
        'Which countries would you like to view?',
        countries,
        ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

    # Filter the data
    filtered_gdp_df = gdp_df[
        (gdp_df['Country Code'].isin(selected_countries))
        & (gdp_df['Year'] <= to_year)
        & (from_year <= gdp_df['Year'])
    ]

    st.header('GDP over time', divider='gray')

    # Display the line chart
    st.line_chart(
        filtered_gdp_df,
        x='Year',
        y='GDP',
        color='Country Code',
    )

    first_year = gdp_df[gdp_df['Year'] == from_year]
    last_year = gdp_df[gdp_df['Year'] == to_year]

    st.header(f'GDP in {to_year}', divider='gray')

    cols = st.columns(4)

    for i, country in enumerate(selected_countries):
        col = cols[i % len(cols)]

        with col:
            first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
            last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

            if math.isnan(first_gdp):
                growth = 'n/a'
                delta_color = 'off'
            else:
                growth = f'{last_gdp / first_gdp:,.2f}x'
                delta_color = 'normal'

            st.metric(
                label=f'{country} GDP',
                value=f'{last_gdp:,.0f}B',
                delta=growth,
                delta_color=delta_color
            )

# -----------------------------------------------------------------------------
# Display the login screen or main app based on login status
if login():
    main_app()
