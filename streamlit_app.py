import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Set the title and favicon for the browser tab.
st.set_page_config(page_title="GDP and Inventory Dashboard", page_icon=":earth_americas:")

# -----------------------------------------------------------------------------
# Step 1: Display the GDP Dashboard

@st.cache_data
def get_gdp_data():
    """Fetch GDP data."""
    gdp_file = Path(__file__).parent / "gdp_data.csv"  # Using relative path for GDP data
    gdp_df = pd.read_csv(gdp_file)
    return gdp_df

# Display GDP data and chart
gdp_df = get_gdp_data()

st.title("GDP Dashboard")
st.write("Browse GDP data from various countries.")

st.line_chart(gdp_df, x="Country", y="GDP")

# -----------------------------------------------------------------------------
# Step 2: User Login Form for Inventory Access


def get_user_credentials():
    """Extract credentials from Streamlit secrets."""
    credentials = {}
    for user_key in st.secrets["credentials"]:
        user_info = st.secrets["credentials"][user_key]
        credentials[user_info["username"]] = {
            "password": user_info["password"]  # We only need to check the password now
        }
    return credentials

user_credentials = get_user_credentials()

# Login form
st.subheader("Login for Inventory Data")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Step 3: Verify login and display inventory data
if st.button("Login"):
    if username in user_credentials and password == user_credentials[username]["password"]:
        st.success(f"Welcome {username}!")

        # Automatically load the CSV based on the username (e.g., user1.csv, user2.csv)
        inventory_file = Path(__file__).parent / f"{username}.csv"  # Username-based CSV file
        try:
            inventory_df = pd.read_csv(inventory_file)

            # Display the inventory table
            st.subheader(f"Inventory for {username}")
            st.dataframe(inventory_df)

            # Display inventory charts (e.g., Units Left and Best Sellers)
            st.subheader("Units Left")
            need_to_reorder = inventory_df[inventory_df["units_left"] < inventory_df["reorder_point"]].loc[:, "item_name"]
            if len(need_to_reorder) > 0:
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
