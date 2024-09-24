import requests

BASE_URL = "http://127.0.0.1:8000"  # Backend URL


# 1. Submit a listing with an image, title, description, and price
def submit_listing(image, title, description, price, reasoning):
    url = f"{BASE_URL}/listing"
    files = {"image": image}
    data = {"title": title, "description": description, "price": price, "reasoning": reasoning}

    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# 2. Fetch all rules
def get_rules():
    url = f"{BASE_URL}/rules"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# 3. Add a new rule
def add_rule(rule):
    url = f"{BASE_URL}/rule"
    try:
        response = requests.post(url, json={"content": rule})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# 4. Delete a rule by ID
def delete_rule(rule_id):
    url = f"{BASE_URL}/rule/{rule_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# 5. Fetch all listings
def get_listings():
    url = f"{BASE_URL}/listings"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    # 2. Delete a listing by ID


def delete_listing(listing_id):
    url = f"{BASE_URL}/listing/{listing_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def check_listing(image, title, description, price):
    url = f"{BASE_URL}/check-listing"
    files = {"image": image}
    data = {"title": title, "description": description, "price": price}

    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}