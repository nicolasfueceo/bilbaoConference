from fastapi import FastAPI, HTTPException, UploadFile, File
from uuid import uuid4
import firebase_admin
from firebase_admin import credentials, firestore, storage
from backend.src.models import Listing
from fastapi.responses import JSONResponse

from fastapi import Form
from backend.src.models import Rule
from backend.src.firebase_utils import db, bucket
from backend.src.moderator.moderator import process_listing
from typing import Optional
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

# Collection names in Firestore
LISTINGS_COLLECTION = "listings"
RULES_COLLECTION = "rules"


def upload_image_to_firebase(image_file: UploadFile):
    # Generate a unique filename for the image
    image_filename = f"{uuid4()}.jpg"  # You can modify the file extension as needed

    # Upload the image to Firebase Storage
    blob = bucket.blob(image_filename)
    blob.upload_from_file(image_file.file, content_type=image_file.content_type)

    # Make the file publicly accessible and return its URL
    blob.make_public()
    return blob.public_url


# Helper function to get Firestore document
def get_document(collection_name, doc_id):
    doc_ref = db.collection(collection_name).document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")


# Helper function to delete Firestore document
def delete_document(collection_name, doc_id):
    doc_ref = db.collection(collection_name).document(doc_id)
    if doc_ref.get().exists:
        doc_ref.delete()
    else:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")


# 1. POST /listing: Submit a new listing
@app.post("/listing")
async def create_listing(
        image: UploadFile = File(...),  # Binary image file upload
        title: str = Form(...),  # Title, price, and description passed as form data
        description: str = Form(...),
        price: float = Form(...),
        reasoning: str = Form(...)  # Add reasoning from moderation
):
    try:
        # Upload the image to Firebase Storage and get its URL
        image_url = upload_image_to_firebase(image)

        # Generate unique ID for the listing
        listing_id = str(uuid4())

        # Create the listing data with image URL, price, and reasoning
        listing_data = {
            "id": listing_id,
            "title": title,
            "description": description,
            "price": price,
            "image_url": image_url,
            "reasoning": reasoning  # Add reasoning to listing data
        }

        # Store listing in Firestore
        db.collection("listings").document(listing_id).set(listing_data)

        return {"message": "Listing created", "id": listing_id, "image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 2. GET /listings: Return all listings
@app.get("/listings")
async def get_all_listings():
    listings_ref = db.collection(LISTINGS_COLLECTION)
    listings = [doc.to_dict() for doc in listings_ref.stream()]
    return {"listings": listings}


# 4. GET /rules: Return all rules
@app.get("/rules")
async def get_rules():
    rules_ref = db.collection(RULES_COLLECTION)
    rules = [doc.to_dict() for doc in rules_ref.stream()]
    return {"rules": rules}


@app.post("/check-listing")
async def check_listing(
        title: str = Form(...),
        description: Optional[str] = Form(None),
        image: UploadFile = File(...),
        price: float = Form(...)
):
    """
    POST /check-listing
    This endpoint takes the listing title, description, price, and image, and processes them to determine if the listing should be flagged.
    If the listing is not flagged (action=False), it automatically uploads the listing.

    Args:
    - title (str): The title of the listing.
    - description (Optional[str]): The description of the listing.
    - image (UploadFile): The image file uploaded by the user.
    - price (float): The price of the listing.

    Returns:
    - JSON response with reasoning and action (True/False).
    """
    try:
        # Read the image bytes
        image_bytes = await image.read()

        # Call the process_listing function to handle the moderation
        response = process_listing(title, description, image_bytes)

        if not response:
            raise HTTPException(status_code=500, detail="Failed to process the listing")

        # If action is False (listing is not flagged), upload the listing
        if not response["action"]:
            image.file.seek(0)
            image_url = upload_image_to_firebase(image)

            # Create the listing data
            listing_id = str(uuid4())
            listing_data = {
                "id": listing_id,
                "title": title,
                "description": description,
                "price": price,
                "image_url": image_url,
                "reasoning": response["reasoning"]  # Store the reasoning with the listing
            }

            # Store listing in Firestore
            db.collection("listings").document(listing_id).set(listing_data)

            # Include the listing ID in the response
            response["listing_id"] = listing_id
            response["image_url"] = image_url

        # Return the response in JSON format
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error in /check-listing: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 5. POST /rule: Add a new rule to the DB
@app.post("/rule")
async def add_rule(rule: Rule):
    rule_id = str(uuid4())  # Generate unique ID for the rule
    rule_data = rule.dict()
    rule_data["id"] = rule_id
    db.collection(RULES_COLLECTION).document(rule_id).set(rule_data)
    return {"message": "Rule added", "id": rule_id}


# 6. DELETE /rule/{id}: Delete a rule by ID
@app.delete("/rule/{id}")
async def delete_rule(id: str):
    delete_document(RULES_COLLECTION, id)
    return {"message": f"Rule with ID {id} deleted"}


@app.delete("/listing/{listing_id}")
async def delete_listing(listing_id: str):
    try:
        doc_ref = db.collection("listings").document(listing_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

        doc_ref.delete()
        return {"message": f"Listing with ID {listing_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
