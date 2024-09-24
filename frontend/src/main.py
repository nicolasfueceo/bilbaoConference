import streamlit as st
from frontend.pages.listings import display_listings
from frontend.pages.upload_content import upload_content
from frontend.pages.exclusion_list import exclusion_list


# Main Streamlit app configuration
st.set_page_config(page_title="AIBay Content Moderation", page_icon="🔥", layout="wide")

# Add the AIBay logo
st.image("frontend/assets/aibay.png", use_column_width=True)

# Brief of the situation for the user
st.markdown(
    """
    <div style='text-align: left; font-size: 24px; font-weight: bold;'>
        Welcome to AIBay - your AI-powered eCommerce platform
    </div>
    <p style='font-size: 18px;'>
        As a business owner of an ecommerce platform allowing users to resell items, you face the challenge of moderating thousands of listings to prevent scams and non-compliant content. 
        With the sheer volume of items being uploaded, keeping track of fraudulent or harmful content manually is no longer feasible. 
        Here at AIBay, we provide an AI-powered solution to help you automatically moderate listings and ensure compliance with your terms and conditions.
    </p>
    """,
    unsafe_allow_html=True
)
# Create tabs
tab1, tab2, tab3 = st.tabs(["Listings", "Upload Content", "Exclusion List"])

# Tab 1: Display Listings
with tab1:
    display_listings()

# Tab 2: Upload Content
with tab2:
    upload_content()

# Tab 3: Exclusion List
with tab3:
    exclusion_list()
