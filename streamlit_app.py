import streamlit as st
import pandas as pd
import altair as alt

# Set the title and favicon for the browser tab.
st.set_page_config(page_title="GDP and Inventory Dashboard", page_icon=":earth_americas:")

# -----------------------------------------------------------------------------
# Step 1: Display the GDP Dashboard

@st.cache_data
def get_gdp_data():
    """Fetch GDP data."""
    # Replace this with actual path to your CSV or another data source.
    data = {
        "Country": ["USA", "China", "Germany", "Brazil", "India"],
        "Year": [2020, 2020, 2020, 2020, 2020],
        "GDP": [21000, 14100, 3845, 2050, 2875],
    }
    return pd.DataFrame(data)

# Display GDP data and chart
gdp_df = get_gdp_data()

st.title("GDP Dashboard")
st.write("Browse GDP data from various countries.")

st.line_chart(gdp_df, x="Country", y="GDP")

# -----------------------------------------------------------------------------
# Step 2: User Login Form for Inventory Access

# Use Streamlit secrets to retrieve user credentials and datasets
# Example secrets structure in .streamlit/secrets.toml:
# [credentials.user1]
# username = "user1"
# password = "password1"
# dataset = "/mnt/data/user1_inventory.csv"
#
# [credentials.user2]
# username = "user2"
# password = "password2"
# dataset = "/mnt/data/user2_inventory.csv"
#
# [credentials.user3]
# username = "user3"
# password = "password3"
# dataset = "/mnt/data/user3_inventory.csv"

def get_user_credentials():
    """Extract credentials and datasets from Streamlit secrets."""
    credentials = {}
    for user_key in st.secrets["credentials"]:
        user_info = st.secrets["credentials"][user_key]
        credentials[user_info["username"]] = {
            "password": user_info["password"],
            "dataset": user_info["dataset"]
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

        # Load the inventory data for the specific user
        inventory_path = user_credentials[username]["dataset"]
        inventory_df = pd.read_csv(inventory_path)

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
    else:
        st.error("Incorrect username or password. Please try again.")
