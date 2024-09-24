import streamlit as st
from frontend.utils.api_utils import check_listing

def upload_content():
    st.title("Upload Content")
    st.subheader("Upload your photo, price, and description for moderation")

    # File uploader for image
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    # Text area for product description
    title = st.text_input("Enter a title for the image")
    description = st.text_area("Enter a description for the image")
    price = st.number_input("Enter the price", min_value=0.0, step=0.01)

    if st.button("Submit"):
        if uploaded_image and description and title and price:
            # Step 1: Call the check-listing endpoint for moderation
            moderation_result = check_listing(uploaded_image, title, description, price)

            if "error" in moderation_result:
                st.error(f"Error during moderation: {moderation_result['error']}")
            else:
                # Check if listing is flagged by moderation
                if moderation_result["action"]:
                    st.error(f"Listing rejected due to: {moderation_result['reasoning']}")
                else:
                    # Success message if listing is uploaded (since action is False)
                    st.success(f"Content submitted successfully! Listing ID: {moderation_result['listing_id']}")
                    st.image(moderation_result["image_url"], caption="Uploaded Image", use_column_width=True)
        else:
            st.error("Please upload an image, provide a title, description, and price.")
