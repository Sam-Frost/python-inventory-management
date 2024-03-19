import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


current_dir = os.path.dirname(__file__)
firebase_json_path = os.path.join(current_dir, "firebase.json")

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_json_path)
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

def create_document(collection_name, data):
    try:
        # Create a reference to the collection
        collection_ref = db.collection(collection_name)

       # Add the document to the collection
        result = collection_ref.add(data)

        # Extract document reference object from the result tuple
        document_ref = result[1]

        print("Document created with ID:", document_ref.id)
        return document_ref.id
        # return result

    except Exception as e:
        print("An error occurred:", e)
        return None
    

res = create_document("test", {'naame': 'test'})

print(res)