import streamlit as st
from frontend.utils.api_utils import get_listings, delete_listing

def display_listings():
    st.title("Listings")
    st.subheader("Browse all available listings")

    # Fetch all listings from the backend
    listings_data = get_listings()

    if "error" in listings_data:
        st.error(f"Error fetching listings: {listings_data['error']}")
    else:
        listings = listings_data.get("listings", [])
        if not listings:
            st.write("No listings available.")
        else:
            # Display listings in a more polished layout
            for listing in listings:
                with st.container():  # Use container to separate each listing
                    # Define the layout with two columns
                    with st.container():
                        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 3])

                        # Column 1: Image
                        with col1:
                            st.image(listing['image_url'], use_column_width=True, caption=listing['title'], width=150)

                        # Column 2: Title, Price, Description, and Reasoning
                        with col2:
                            st.markdown(f"### {listing['title']}")
                            st.markdown(f"**Price:** ${listing['price']}")
                            st.markdown(f"Description: {listing['description']}")
                            st.markdown(f"**Reasoning:** {listing.get('reasoning', 'No reasoning available')}")
                            st.markdown("---")

                            # Delete button aligned to the right
                            if st.button(f"Delete {listing['id']}", key=f"delete_{listing['id']}"):
                                delete_result = delete_listing(listing['id'])
                                if "error" in delete_result:
                                    st.error(f"Error deleting listing: {delete_result['error']}")
                                else:
                                    st.success(f"Listing {listing['id']} deleted successfully!")
                                    st.rerun()  # Refresh page after deletion
                        st.markdown('</div>', unsafe_allow_html=True)
