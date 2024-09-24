import firebase_admin
from firebase_admin import credentials, firestore, storage




# Use the credentials JSON file you downloaded from Firebase
cred = credentials.Certificate('backend/config/creds.json')
firebase_admin.initialize_app(cred,
                              {
                                  'storageBucket': 'bilbaopresentation.appspot.com'
                              })

# Initialize Firestore
db = firestore.client()
bucket = storage.bucket()
